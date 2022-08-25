import asyncio
import json
import os
import uuid
from copy import deepcopy
from typing import List, Dict
from time import time as timer
from datetime import timedelta, datetime

import aiofiles
from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from src_1.external_data.database import get_addresses, get_all_transactions_hash
from src_1.external_data.es_send import send_exception_to_kibana, send_msg_to_kibana
from src_1.utils import (
    to_base58check_address, from_sun, convert_time, TronAccountAddress, get_asset_trc20,
    get_transaction_for_fee, send_to_rabbit_mq, get_transaction_in_db, send_to_rabbit_mq_balancer
)
from config import (
    LAST_BLOCK, USDT, USDC, AdminAddress, ReportingAddress,
    logger, decimals, node, network, ERROR, NOT_SEND, NOT_SEND_TO_TRANSACTION
)


AdminAddresses = [AdminAddress, ReportingAddress]


class TransactionDemon:
    # Provider config
    __provider = AsyncHTTPProvider(node)
    # Network
    __network = network

    def __init__(self):
        """Connect to Tron Node"""
        self.node = AsyncTron(
            provider=self.__provider if self.__network == "mainnet" else None,
            network=self.__network
        )
        self.public_node = AsyncTron(
            provider=AsyncHTTPProvider(api_key="16c3b7ca-d498-4314-aa1d-a224135faa26") if self.__network == "mainnet" else None,
            network=self.__network
        )

    async def get_node_block_number(self) -> int:
        """Get the number of the private block in the node"""
        try:
            return int(await self.node.get_latest_block_number())
        except Exception as error:
            logger.error(f"ERROR: {error}")
            return int(await self.public_node.get_latest_block_number())

    async def get_last_block_number(self):
        """Get the block number recorded in the "last_block.txt" file"""
        async with aiofiles.open(LAST_BLOCK, "r") as file:
            last_block = await file.read()
        if last_block:
            return int(last_block)
        else:
            return await self.get_node_block_number()

    async def save_block_number(self, block_number: int):
        """
        Save the current block to a file "last_block.txt"
        :param block_number: The number of the block to be recorded
        """
        async with aiofiles.open(LAST_BLOCK, "w") as file:
            await file.write(str(block_number))

    async def smart_contract_transaction(self, data: str, contract_address: TronAccountAddress) -> Dict:
        """
        Unpacking a smart contract
        :param data: Smart Contract Information
        :param contract_address: Smart contract (Token TRC20) address
        """
        token_dict = await get_asset_trc20(address=contract_address)
        amount = decimals.create_decimal(int("0x" + data[72:], 0) / 10 ** int(token_dict["decimals"]))
        to_address = to_base58check_address("41" + data[32:72])
        token_symbol, token_name = token_dict["symbol"], token_dict["name"]
        return {
            "to_address": to_address,
            "token": token_symbol,
            "name": token_name,
            "amount": "%.8f" % amount
        }

    async def processing_block(self, block_number: int, addresses: List[TronAccountAddress]):
        """
        This method receives transactions from the block and processes them
        :param block_number: The number of the block from which to receive transactions
        :param addresses: A list of addresses to search for transactions
        """
        try:
            logger.error(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | PROCESSING BLOCK: {block_number}")
            # Get transactions from the block.
            try:
                block = await self.node.get_block(id_or_num=int(block_number))
            except Exception as error:
                logger.error(f"ERROR: {error}")
                block = await self.public_node.get_block(id_or_num=int(block_number))
            if "transactions" in block.keys() and isinstance(block["transactions"], list):
                count_trx = len(block["transactions"])
            else:
                return True
            if count_trx == 0:
                return True
            all_transactions_hash_in_db = await get_all_transactions_hash()
            tnx = await asyncio.gather(*[
                self.processing_transaction(
                    tx=block['transactions'][index],
                    addresses=addresses,
                    timestamp=block["block_header"]["raw_data"]["timestamp"],
                    all_transactions_hash_in_db=all_transactions_hash_in_db
                )
                for index in range(count_trx)
            ])
            tnx = list(filter(lambda x: x is not None, tnx))
            if len(tnx) > 0:
                await asyncio.gather(*[
                    self.send_to_rabbit(
                        package=tx,
                        addresses=addresses,
                        all_transactions_hash_in_db=all_transactions_hash_in_db,
                        block_number=block_number
                    ) for tx in tnx
                ])
            return True
        except Exception as error:
            await send_exception_to_kibana(error, "BLOCK ERROR")
            return False

    async def processing_transaction(self, tx: Dict, addresses: List[TronAccountAddress],
                                     timestamp: int, all_transactions_hash_in_db: List):
        """
        This method analyzes transactions in detail, and searches for the necessary addresses in them.
        :param tx: The transaction that needs to be parsed
        :param addresses: A list of addresses to search for transactions
        :param timestamp: The time of confirmation of the transaction in the block
        :param all_transactions_hash_in_db: Hash of transactions that are in the database
        """
        try:
            # If the transaction is not confirmed or with an error, then skip it.
            if tx["ret"][0]["contractRet"] != "SUCCESS":
                return None
            # Value in the transaction
            tx_values = tx["raw_data"]["contract"][0]["parameter"]["value"]
            # Transaction type
            tx_type = tx["raw_data"]["contract"][0]["type"]
            token = None
            # Transaction hash
            tx_hash = tx["txID"]
            # Addresses that are in the transaction.
            tx_addresses = []
            tx_from = None  # Sender
            tx_to = None    # Receiver
            if tx_values["owner_address"] is not None:
                # Recording the sender
                tx_from = to_base58check_address(tx_values["owner_address"])
                tx_addresses.append(tx_from)
            if tx_type == "TransferContract" and tx_values["to_address"] is not None:
                # We record the recipient if the transaction was made in the native currency.
                tx_to = to_base58check_address(tx_values["to_address"])
                tx_addresses.append(tx_to)
            elif tx_type == "TriggerSmartContract" and tx_values["contract_address"] in [USDC, USDT] \
                    and tx_values["data"] is not None and 140 > len(tx_values["data"]) > 130:
                # We record the recipient if the transaction was made in tokens.
                tx_to = to_base58check_address("41" + tx_values["data"][32:72])
                tx_addresses.append(tx_to)

            address = None
            for tx_address in tx_addresses:
                # We are looking for the address of our wallet among the addresses in the transaction.
                if tx_address in addresses:
                    # If we find it, we write it to a variable.
                    address = tx_address
                    break

            if address is not None or tx_hash in all_transactions_hash_in_db:
                if address is None:
                    address = tx_from
                if tx_type == "TransferContract":
                    amount = "%.8f" % decimals.create_decimal(from_sun(tx_values["amount"]))
                elif tx_type == "TriggerSmartContract":
                    # We analyze data transactions.
                    token = await self.smart_contract_transaction(
                        data=tx_values["data"],
                        contract_address=tx_values["contract_address"]
                    )
                    if "data" in token:
                        return None
                    amount = token["amount"]
                else:
                    amount = 0
                # We get a more detailed transaction.
                try:
                    tx_fee = await self.node.get_transaction_info(tx_hash)
                except Exception as error:
                    logger.error(f"ERROR: {error}")
                    tx_fee = await self.public_node.get_transaction_info(tx_hash)
                if "fee" not in tx_fee:
                    fee = "0"
                else:
                    fee = "%.8f" % decimals.create_decimal(from_sun(tx_fee["fee"]))
                values = {
                    "time": timestamp,
                    "datetime": str(convert_time(int(str(timestamp)[:10]))),
                    "transactionHash": tx_hash,
                    "amount": amount,
                    "fee": fee,
                    "senders": [{
                        "address": tx_from,
                        "amount": amount
                    }],
                    "recipients": [{
                        "address": tx_to,
                        "amount": amount,
                    }],
                }
                if token is not None and "data" not in token:
                    # If the transaction was made in a token.
                    values["token"] = token["token"]
                    values["name"] = token["name"]
                return {"address": address, "transactions": [values]}
            return None
        except Exception as error:
            await send_exception_to_kibana(error, f'PROC TX ERROR: {error}')
            return None

    async def send_to_rabbit(self, package, addresses, all_transactions_hash_in_db, block_number) -> None:
        """
        We are preparing transactions to be sent to RabbitMQ
        :param package: Ready transaction
        :param addresses: A list of addresses to search for transactions
        :param all_transactions_hash_in_db: Hash of transactions that are in the database
        :param block_number: Block number
        """
        token = (
            package["transactions"][0]["token"].lower()
            if "token" in package['transactions'][0].keys()
            else "trx"
        )
        if token is not None and token != "trx":
            tx_network = f"tron_trc20_{token}"
        else:
            tx_network = "tron"
        # We pack the transaction in a gift box.
        package_for_sending = [
            {
                "network": tx_network,
                "block": block_number
            },
            package
        ]
        try:
            recipient = package['transactions'][0]['recipients'][0]['address']
            sender = package['transactions'][0]['senders'][0]['address']

            if sender in AdminAddresses and (token in [None, "trx", "TRX"]) and (recipient in addresses):
                """
                If the transaction was made from the admin, and it was not a token transaction, and the recipient
                in this transaction was our address, then the transaction was most likely made to pay the commission.
                """
                tx = get_transaction_for_fee(transaction=package_for_sending[1])
                package_for_sending[1]["address"] = tx["senders"][0]["address"]
                package_for_sending[1]["transactions"] = [tx]
                await send_to_rabbit_mq(values=json.dumps(package_for_sending))
                await send_msg_to_kibana(msg=f'TX WITH FEE FOR SENDING TO MAIN WALLET: {package}')
            elif sender in AdminAddresses and (recipient not in addresses):
                """
                If the transaction was sent from the admin address, and the recipient is not our address,
                then most likely these are withdrawal transactions to someone else's wallet.
                """
                tx_hash = package["transactions"][0]["transactionHash"]
                if tx_hash in all_transactions_hash_in_db:
                    # If this transaction is in the database, then we will record it separately
                    package_for_sending[1]["transactions"][0] = get_transaction_in_db(
                        transaction=package["transactions"][0],
                        transaction_hash=tx_hash
                    )
                    # And also send it separately
                    await self.send_dummy_tx_with_fee_after_sending(package_for_sending)
                await send_to_rabbit_mq(values=json.dumps(package_for_sending))
                await send_msg_to_kibana(f'SENDING FROM MAIN WALLET: {package_for_sending}')
            elif recipient not in AdminAddresses:
                """
                If the recipient is not an admin wallet, then this transaction is from someone
                else's wallet to our wallet.
                """
                await send_to_rabbit_mq(values=json.dumps(package_for_sending))
                # We will send the transaction data to the balancer for debiting funds.
                await send_to_rabbit_mq_balancer(values=json.dumps([{"address": recipient, "token": token.upper()}]))
                await send_msg_to_kibana(f'RECEIVE NEW TX: {package_for_sending}')
        except Exception as error:
            await send_exception_to_kibana(error, f'SENDING TO MQ ERROR: {package_for_sending}')
            async with aiofiles.open(ERROR, 'a', encoding='utf-8') as file:
                # If an error occurred on the RabbitMQ side, write about it.
                await file.write(f"Error: {package_for_sending} | RabbitMQ not responding {error} \n")
            new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
            async with aiofiles.open(new_not_send_file, 'w') as file:
                # Write all the verified data to a json file, and do not praise the work
                await file.write(json.dumps(package_for_sending))

    async def send_dummy_tx_with_fee_after_sending(self, package: List[Dict]):
        """
        The formation of a fictional transaction for charging fee to the administrator.
        :param package: A packaged transaction.
        """
        dummy = [
            {"network": 'tron', "block": package[0]['block']},
            deepcopy(package[1])
        ]
        dummy[1]['transactions'][0]['transactionHash'] = str(uuid.uuid4().hex)
        dummy[1]['transactions'][0]['amount'] = dummy[1]['transactions'][0]['fee']
        dummy[1]['transactions'][0]['fee'] = 0
        dummy[1]['transactions'][0]['recipients'] = []
        dummy[1]['transactions'][0]['senders'] = [{
            'address': ReportingAddress,
            'amount': dummy[1]['transactions'][0]['amount']
        }]
        await send_msg_to_kibana(msg=f'DUMMY TX FOR NODE FEE AFTER SENDING: {dummy}')
        await send_to_rabbit_mq(values=json.dumps(dummy))

    async def run(self):
        """The script runs all the time"""
        start = await self.get_last_block_number()
        pack_size = 1
        while True:
            end = await self.get_node_block_number()
            if end - start < pack_size:
                await asyncio.sleep(3)
            else:
                start_time = timer()
                addresses = await get_addresses()
                success = await asyncio.gather(*[
                    self.processing_block(block_number=block_number, addresses=addresses)
                    for block_number in range(start, start + pack_size)
                ])
                logger.error("End block: {}. Time taken: {} sec".format(
                    start, str(timedelta(seconds=int(timer() - start_time)))
                ))
                if all(success):
                    start += pack_size
                    await self.save_block_number(block_number=start)
                else:
                    await send_msg_to_kibana(f'BLOCK {start} ERROR. RUN BLOCK AGAIN')
                    continue

    async def start_in_range(self, start_block: int, end_block: int, list_addresses=None):
        for block_number in range(start_block, end_block):
            if list_addresses is not None:
                addresses = list_addresses
            else:
                addresses = await get_addresses()
            await self.processing_block(block_number=block_number, addresses=addresses)

    async def start_in_list_block(self, list_blocks: List[int]):
        for block_number in list_blocks:
            addresses = await get_addresses()
            await self.processing_block(block_number=int(block_number), addresses=addresses)

    async def start(self, start_block: int = None, end_block: int = None, list_blocks: List[int] = None, list_addresses: List[TronAccountAddress] = None):
        logger.error((
            "Start of the search: "
            f"Start block: {start_block if start_block is not None else 'Not specified'} | "
            f"End block: {end_block if end_block is not None else 'Not specified'} | "
        ))
        if list_blocks:
            await self.start_in_list_block(list_blocks=list_blocks)
        elif start_block and end_block:
            await self.start_in_range(start_block, end_block)
        elif start_block and not end_block:
            await self.start_in_range(start_block, await self.get_node_block_number() + 1)
        elif not start_block and end_block:
            await self.start_in_range(await self.get_node_block_number(), end_block)
        else:
            await send_msg_to_kibana(f"DEMON IS STARTING")
            await self.send_all_from_folder_not_send()
            await self.run()
        logger.error("End of search")

    async def send_all_from_folder_not_send(self):
        """Send those transits that were not sent due to any errors"""
        files = os.listdir(NOT_SEND)
        for file_name in files:
            try:
                path = os.path.join(NOT_SEND, file_name)
                async with aiofiles.open(path, 'r') as file:
                    values = await file.read()
                await send_to_rabbit_mq(values=values)
                os.remove(path)
            except Exception as error:
                logger.error(f"Error: {error}")
                logger.error(f"Not send: {file_name}")
                continue
        files = os.listdir(NOT_SEND_TO_TRANSACTION)
        for file_name in files:
            try:
                path = os.path.join(NOT_SEND, file_name)
                async with aiofiles.open(path, 'r') as file:
                    values = await file.read()
                await send_to_rabbit_mq_balancer(values=values)
                os.remove(path)
            except Exception as error:
                logger.error(f"Error: {error}")
                logger.error(f"Not send: {file_name}")
                continue
