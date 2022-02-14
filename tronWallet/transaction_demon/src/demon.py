import asyncio
import time
from typing import List, Dict
from time import time as timer
from datetime import timedelta, datetime as dt

import tronpy.exceptions
from tronpy.tron import Tron, HTTPProvider

from src.token_db import smart_contract_transaction
from src.demon_to_send import export_transactions, send_all_from_folder_not_send
from src.utils import to_base58check_address, from_sun, convert_time, TronAccountAddress
from src.external_data.database import get_addresses, get_all_transactions_hash
from config import LAST_BLOCK, USDT, USDC, AdminAddress, ReportingAddress, logger, decimals, node, network

class TransactionDemon:
    # Provider config
    __provider: dict = HTTPProvider(node)
    # Network
    __network = network

    def __init__(self):
        """Connect to Tron Node"""
        self.node = Tron(
            provider=self.__provider if self.__network == "mainnet" else None,
            network=self.__network
        )

    @property
    def get_block_number(self) -> int:
        """Get block number"""
        return int(self.node.get_latest_block_number())

    def __get_block_transactions(self, block: int = None) -> dict:
        """
        Returns a block with transaction
        :param block: Block number
        """
        if not block:
            block = self.get_block_number
            with open(LAST_BLOCK, "r") as file:
                # We read from the file if the last block is more than 2, then we take it away,
                # if it has not changed in any way, then we wait.
                last_block = file.read()
            logger.error("Start processing transactions")
            if last_block:
                last_block = int(last_block)
                # Will wait until a new block appears
                while block == last_block:
                    time.sleep(2)
                    block = self.get_block_number
                    logger.error(f"Block now: {block} | Last block in file: {last_block}")
                    # If the block has increased by more than zero, then go to the next block.
                if block - last_block > 0:
                    block = last_block + 1
            logger.error("End processing transactions")
            with open(LAST_BLOCK, "w") as file:
                # Writing down the last block
                logger.error(f"Write to {LAST_BLOCK} new number: {block}")
                file.write(str(block))
        else:
            if block > self.get_block_number:
                last_block = self.get_block_number
                while block != last_block:
                    time.sleep(2)
                    last_block = self.get_block_number
        try:
            return self.node.get_block(id_or_num=int(block))
        except tronpy.exceptions.BlockNotFound as error:
            time.sleep(20)
            return self.node.get_block(id_or_num=int(block))

    async def __script(self, block_trx: dict, addresses: List[TronAccountAddress]) -> None:
        """
        Searching for the right transactions
        :param block_trx: Block with transactions
        :param addresses: The addresses to search for.
        """
        block_number = int(block_trx['block_header']['raw_data']['number'])
        # All transactions will be stored here
        __all_transactions_to_send_to_rabbit_mq = []
        # Checks if there are transactions in the block
        if "transactions" in block_trx.keys() and isinstance(block_trx["transactions"], list):
            transactions_count = len(block_trx["transactions"])
        else:
            logger.error(f"Block: {block_number} is not have transactions!!")
            time.sleep(2)
            return
        list_transactions = await asyncio.gather(*[
            self.__processing_transactions(
                transactions=block_trx["transactions"][right_border: (right_border + 1)],
                addresses=addresses, timestamp=block_trx["block_header"]["raw_data"]["timestamp"]
            )
            for right_border in range(transactions_count)
        ])
        for transactions in list_transactions:
            __all_transactions_to_send_to_rabbit_mq.extend(transactions)
        # Export transactions
        if len(__all_transactions_to_send_to_rabbit_mq) > 0:
            export_transactions(
                all_transactions=__all_transactions_to_send_to_rabbit_mq,
                block_number=block_number,
                addresses=addresses
            )

    async def __processing_transactions(
            self, transactions: dict, addresses: List[TronAccountAddress], timestamp: int) -> List:
        """
        Unpacking transactions and checking for the presence of required addresses in them
        :param transactions: Set of transactions
        :param addresses: The address to search for
        :param timestamp: Block appearance time
        """
        funded_trx_for_sending = []
        all_transactions_hash_in_db = get_all_transactions_hash()
        for txn in transactions:
            # If the transaction is not approved, then we skip it.
            if txn["ret"][0]["contractRet"] != "SUCCESS":
                continue
            txn_values = txn["raw_data"]["contract"][0]["parameter"]["value"]
            txn_type = txn["raw_data"]["contract"][0]["type"]
            addresses_in_transaction = []
            try:
                # This field is present in all transactions. Fields of the owner (sender) of the transaction
                if txn_values["owner_address"] is not None:
                    addresses_in_transaction.append(to_base58check_address(txn_values["owner_address"]))
                # If the transfer transaction is TRX
                if txn_type == "TransferContract" and txn_values["to_address"] is not None:
                    addresses_in_transaction.append(to_base58check_address(txn_values["to_address"]))
                # If a TRC20 tokens transfer transaction inside a smart contract
                elif txn_type == "TriggerSmartContract" \
                        and txn_values["contract_address"] in [USDC, USDT] \
                        and txn_values["data"] is not None \
                        and 150 > len(txn_values["data"]) > 100:
                    addresses_in_transaction.append(to_base58check_address("41" + txn_values["data"][32:72]))
            except Exception as error:
                logger.error(f"Error Step 139: {error}\nTX: {txn['txID']} Data: {txn_values['data']}")
                raise error
            address = None
            for address_in_transaction in addresses_in_transaction:
                if address_in_transaction in addresses or address_in_transaction == AdminAddress \
                        or address_in_transaction == ReportingAddress:
                    address = address_in_transaction
                    break
            if address is not None or txn["txID"] in all_transactions_hash_in_db:
                funded_trx_for_sending.append(await self.__packaging_for_dispatch(
                    txn=txn,
                    txn_type=txn_type,
                    timestamp=timestamp
                ))
            else:
                continue
        return funded_trx_for_sending

    async def __packaging_for_dispatch(self, txn: dict, txn_type: str, timestamp: int) -> Dict:
        """
        Packaging the necessary transaction to send to RabbitMQ
        :param txn: Transaction
        :param txn_type: Transaction type
        :param timestamp: Time of sending the transaction
        """
        try:
            txn_values = txn["raw_data"]["contract"][0]['parameter']["value"]
            fee = 0
            if "fee_limit" in txn["raw_data"]:
                try:
                    fee_limit = self.node.get_transaction_info(txn["txID"])
                    if "fee" not in fee_limit:
                        raise Exception
                    fee = "%.8f" % decimals.create_decimal(from_sun(fee_limit["fee"]))
                except Exception as error:
                    logger.error(f"{error}")
                    fee = 0
            values = {
                "time": timestamp,
                "datetime": str(convert_time(int(str(timestamp)[:10]))),
                "transactionHash": txn["txID"],
                "transactionType": txn_type,
                "fee": fee,
                "amount": 0,
                "senders": [
                    {
                        "address": txn_values["owner_address"]
                    }
                ],
                "recipients": []
            }
            # TRX
            if txn_type == "TransferContract":
                amount = "%.8f" % decimals.create_decimal(from_sun(txn_values["amount"]))
                values["amount"] = amount
                values["recipients"] = [{
                    "address": txn_values["to_address"],
                    "amount": amount
                }]
                values["senders"][0]["amount"] = amount
            # TRC20
            else:
                smart_contract = await smart_contract_transaction(
                    data=txn_values["data"], contract_address=txn_values["contract_address"]
                )
                if "data" in smart_contract:
                    values["data"] = smart_contract["data"]
                else:
                    amount = smart_contract["amount"]
                    values["senders"][0]["amount"] = amount
                    values["recipients"] = [{
                        "address": smart_contract["to_address"],
                        "amount": amount
                    }]
                    values["token"] = smart_contract["token"]
                    values["name"] = smart_contract["name"]
                    values["amount"] = amount
            try:
                if txn_type == "TransferContract" \
                        and decimals.create_decimal(values["amount"]) == decimals.create_decimal("0.1"):
                    values["fee"] = "1"
            except Exception as error:
                logger.error(f"{error}")
            return values
        except Exception as error:
            logger.error(f"Error Step 205 packaging for dispatch: {error}")
            return {}

    async def __run(self):
        """The script runs all the time"""
        while True:
            start = timer()
            logger.error(f"Run new iteration: start = {start}")
            # We get a block with transactions
            block_trx = self.__get_block_transactions()

            logger.error("Getting started: {} | Block: {}".format(
                str(dt.now()).split(".")[0], int(block_trx["block_header"]["raw_data"]["number"])
            ))
            # Getting wallets
            addresses = get_addresses()

            # The script itself is run
            await self.__script(block_trx=block_trx, addresses=addresses)

            logger.error("End block: {}. Time taken: {} sec".format(
                int(block_trx["block_header"]["raw_data"]["number"]), str(timedelta(seconds=int(timer() - start)))
            ))

    async def __start_in_range(self, start_block: int, end_block: int):
        """
        Running a script to check range of blocks
        :param start_block: Start with block
        :param end_block: Finish on block
        """
        for block_number in range(start_block, end_block):
            start = timer()
            logger.error(f"Run new iteration: start = {start}")

            logger.error(f"Processing block: {block_number}")
            # We get a block with transactions
            block_trx = self.__get_block_transactions(block=block_number)
            # Getting wallets
            addresses = get_addresses()
            logger.error("Getting started: {} | Block: {}".format(
                str(dt.now()).split(".")[0], int(block_trx["block_header"]["raw_data"]["number"])
            ))
            # The script itself is run
            await self.__script(block_trx=block_trx, addresses=addresses)

            logger.error("End block: {}. Time taken: {} sec".format(
                int(block_trx["block_header"]["raw_data"]["number"]), str(timedelta(seconds=int(timer() - start)))
            ))

    async def start(self, start_block: int = None, end_block: int = None):
        """
        Script Launcher
        :param start_block: Start with block
        :param end_block: Finish on block
        """
        if start_block and end_block:
            await self.__start_in_range(start_block=start_block, end_block=end_block+1)
        elif start_block and not end_block:
            await self.__start_in_range(start_block=start_block, end_block=self.get_block_number + 1)
        elif not start_block and end_block:
            await self.__start_in_range(start_block=self.get_block_number, end_block=end_block+1)
        else:
            send_all_from_folder_not_send()
            await self.__run()