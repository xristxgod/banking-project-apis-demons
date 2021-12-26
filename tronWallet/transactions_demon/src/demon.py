import os
import uuid
import json
import asyncio
import math
import time
from typing import List
from decimal import Decimal
from time import time as timer
from datetime import datetime as dt, timedelta

import tronpy.exceptions
from tronpy.tron import Tron
from tronpy.async_tron import AsyncTron

from .external_data.database import get_addresses
from transactions_demon.src.utils import (
    convert_time, add_into_addresses, send_to_rabbit_mq, send_all_from_folder_not_send
)
from transactions_demon.src.tron_typing import TronAccountAddress, ContractAddress
from transactions_demon.config import (
    async_provider, provider, asyncTronGridApiKey, TronGridApiKey,
    LAST_BLOCK, logger
)

class TransactionDemonConfig:

    # Api key for TronGird
    async_api_key = asyncTronGridApiKey
    api_key = TronGridApiKey

    # Provider config
    config_provider = provider
    async_config_providers = async_provider

class TransactionDemon(TransactionDemonConfig):

    def __init__(self):
        """Connect to Tron Node and async Tron Node"""
        self.__async_node = AsyncTron(provider=self.async_api_key, conf=self.async_config_providers)
        self.__node = Tron(provider=self.api_key, conf=self.config_provider)

    def __get_block_number(self) -> int:
        """Get block number"""
        return int(self.__node.get_latest_block_number())

    def __get_block_transactions(self, block: int = None) -> dict:
        """
        Returns a block with transaction
        :param block: Block number
        """
        if not block:
            block = self.__get_block_number()
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
                    block = self.__get_block_number()
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
            if block > self.__get_block_number():
                last_block = self.__get_block_number()
                while block != last_block:
                    time.sleep(2)
                    last_block = self.__get_block_number()
        try:
            return self.__node.get_block(id_or_num=int(block))
        except tronpy.exceptions.BlockNotFound as error:
            time.sleep(20)
            return self.__node.get_block(id_or_num=int(block))

    async def __script(self, block_trx: dict, addresses: List[TronAccountAddress]) -> None:
        """
        Searching for the right transactions
        :param block_trx: Block with transactions
        :param addresses: The addresses to search for.
        """
        fund_trx_for_send = []

        if "transactions" in block_trx.keys() and isinstance(block_trx["transactions"], list):
            transactions_count = len(block_trx["transactions"])
        else:
            logger.error(f"Block: {block_trx['block_header']['raw_data']['number']} is not have transactions!!")
            time.sleep(2)
            return

        if transactions_count > 15:
            in_split = 7
            list_transactions = await asyncio.gather(*[
                self.__processing_transactions(
                    transactions=block_trx["transactions"][right_border * in_split: (right_border + 1) * in_split],
                    addresses=addresses, timestamp=block_trx["block_header"]["raw_data"]["timestamp"]
                )
                for right_border in range(0, math.ceil(transactions_count / in_split))
            ])
            for transactions in list_transactions:
                fund_trx_for_send.extend(transactions)

            if len(fund_trx_for_send) > 0:
                # Final package of transactions for sending.
                fund_trx_for_send = add_into_addresses(
                    addresses=addresses, funded_trx_for_sending=fund_trx_for_send
                )
            else:
                return
        else:
            fund_trx_for_send = await self.__processing_transactions(
                transactions=block_trx["transactions"],
                addresses=addresses,
                timestamp=block_trx["block_header"]["raw_data"]["timestamp"]
            )

        if len(fund_trx_for_send) > 0:
            fund_trx_for_send.insert(
                0, {"network": "tron", "block": int(block_trx["block_header"]["raw_data"]["number"])}
            )
            send_to_rabbit_mq(values=json.dumps(fund_trx_for_send))

    async def __processing_transactions(self, transactions: dict, addresses: List[TronAccountAddress], timestamp: int) -> list:
        """
        Unpacking transactions and checking for the presence of required addresses in them
        :param transactions: Set of transactions
        :param addresses: The address to search for
        :param timestamp: Block appearance time
        """
        funded_trx_for_sending = []

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
                    addresses_in_transaction.append(
                        self.__node.to_base58check_address(
                            txn_values["owner_address"]
                        )
                    )
                # If the transfer transaction is TRX or TRC10
                if txn_type in ["TransferAssetContract", "TransferContract"]:
                    if txn_values["to_address"] is not None:
                        addresses_in_transaction.append(
                            self.__node.to_base58check_address(
                                txn_values["to_address"]
                            )
                        )
                # If a TRC20 token transfer transaction inside a smart contract
                elif txn_type == "TriggerSmartContract":
                    if txn_values["data"] is not None and 150 > len(txn_values["data"]) > 100:
                        addresses_in_transaction.append(
                            self.__node.to_base58check_address(
                                "41" + txn_values["data"][32:72]
                            )
                        )
                # If the transaction freezes the balance.
                elif txn_type in ["FreezeBalanceContract", "UnfreezeBalanceContract"] \
                        and "receiver_address" in txn_values:
                    addresses_in_transaction.append(
                        self.__node.to_base58check_address(txn_values["receiver_address"])
                    )
                # If the transaction is a vote
                elif txn_type == "VoteWitnessContract" and "vote_address" in txn_values["votes"][0]:
                    try:
                        addresses_in_transaction.append(
                            self.__node.to_base58check_address(txn_values["votes"][0]["vote_address"])
                        )
                    except Exception as error:
                        logger.error(f"Error: {error} | {txn_type} is not add")
                else:
                    pass
            except Exception as error:
                logger.error(f"{error}")
                logger.error(f"TX: {txn['txID']} Data: {txn_values['data']}")
                raise error

            address = None
            for address_in_transaction in addresses_in_transaction:
                if address_in_transaction in addresses:
                    address = address_in_transaction
                    break

            if address is not None:
                funded_trx_for_sending.append(self.__packaging_for_dispatch(
                    txn=txn,
                    txn_type=txn_type,
                    timestamp=timestamp
                ))
            else:
                continue

        return funded_trx_for_sending

    def __packaging_for_dispatch(self, txn: dict, txn_type: str, timestamp: int) -> dict:
        """
        Packaging the necessary transaction to send to RabbitMQ
        :param txn: Transaction
        :param txn_type: Transaction type
        :param timestamp: Time of sending the transaction
        """
        try:
            txn_values = txn["raw_data"]["contract"][0]['parameter']["value"]

            values = {
                "time": timestamp,
                "datetime": str(convert_time(int(str(timestamp)[:10]))),
                "transactionHash": txn["txID"],
                "transactionType": txn_type,
                "fee": str(txn["raw_data"]["fee_limit"] / 1_000_000) if "fee_limit" in txn["raw_data"] else 0,
                "senders": txn_values["owner_address"]
            }
            # TRX or TRC10
            if txn_type in ["TransferContract", "TransferAssetContract"]:
                value = {
                    "recipients": txn_values["to_address"],
                    "amount": str(txn_values["amount"] / 1_000_000),
                }
                if "asset_name" in txn_values:
                    asset = self.__node.get_asset(int(txn_values['asset_name']))
                    value["token"] = f"{asset['name']} ({asset['abbr']})"
            # TRC20
            elif txn_type == "TriggerSmartContract":
                smart_contract = self.__smart_contract_transaction(
                    data=txn_values["data"], contract_address=txn_values["contract_address"]
                )
                value = {
                    "recipients": txn_values["contract_address"],
                    "smartContract": smart_contract
                }
            # Freeze or Unfreeze balance
            elif txn_type in ["FreezeBalanceContract", "UnfreezeBalanceContract"]:
                value = {}
                if "resource" in txn_values:
                    value["resource"] = txn_values["resource"]
                else:
                    value["resource"] = "BANDWIDTH"

                if "frozen_balance" in txn_values:
                    value["amount"] = txn_values["frozen_balance"],
                if "receiver_address" in txn_values:
                    value["recipients"] = txn_values["receiver_address"]
            # Vote
            elif txn_type == "VoteWitnessContract":
                try:
                    value = {
                        "voteAddress": txn_values["votes"][0]["vote_address"],
                        "voteCount": txn_values["votes"][0]["vote_count"]
                    }
                except Exception as error:
                    logger.error(f"{error}")
                    value = {}
            else:
                value = {}
            return {**values, **value}
        except Exception as error:
            logger.error(f"{error}")
            return {}

    def __smart_contract_transaction(self, data: str, contract_address: ContractAddress) -> dict:
        """
        Unpacking a smart contract
        :param data: Smart Contract Information
        :param contract_address: Smart contract (Token TRC20) address
        """
        try:
            contract = self.__node.get_contract(addr=contract_address)
            token_name = f"{contract.name} ({contract.functions.symbol()})"
            decimals = contract.functions.decimals()
            amount = Decimal(value=int("0x" + data[72:], 0) / 10 ** int(decimals))
            to_address = self.__node.to_base58check_address("41" + data[32:72])
            return {
                "toAddress": to_address,
                "token": token_name,
                "amount": str(amount)
            }
        except Exception as error:
            logger.error(f"{error}")
            return {"data": str(data)}

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
            self.__transactions_to_send = []

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
            await self.__start_in_range(start_block=start_block, end_block=end_block)
        elif start_block and not end_block:
            await self.__start_in_range(start_block=start_block, end_block=self.__get_block_number() + 1)
        elif not start_block and end_block:
            await self.__start_in_range(start_block=self.__get_block_number(), end_block=end_block)
        else:
            send_all_from_folder_not_send()
            await self.__run()

