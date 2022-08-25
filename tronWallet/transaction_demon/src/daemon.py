import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict

import aiofiles
from tronpy.tron import TAddress
from tronpy.keys import to_base58check_address

from .core import Core
from .external import DatabaseController
from config import LAST_BLOCK, logger


@dataclass()
class ProcessingTransaction:
    transaction: Dict                      # Transaction Data
    addresses: List[TAddress]              # Addresses in Database
    timestamp: int                         # Time to send transaction
    transactionsHash: List[str]            # Transactions in Database


class FileController:
    @staticmethod
    def get() -> Optional[str]:
        """
        Get data from the file
        :return: Block number
        """
        async with aiofiles.open(LAST_BLOCK, "r") as file:
            return await file.read()

    @staticmethod
    def save(number: int) -> Optional:
        """
        Save data to the file
        :param number: Block number
        """
        async with aiofiles.open(LAST_BLOCK, "w") as file:
            await file.write(str(number))


class Daemon:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Daemon, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.core = Core()

    async def get_node_block_number(self) -> int:
        """Get last block in Blockchain"""
        return self.core.get_latest_block_number()

    async def get_last_block_number(self) -> int:
        """Get last block in file"""
        last_block = FileController.get()
        return await self.get_node_block_number() if not last_block else int(last_block)

    async def processing_block(self, block_number: int, addresses: List[TAddress]) -> Optional:
        """
        This method receives transactions from the block and processes them
        :param block_number: The number of the block from which to receive transactions
        :param addresses: A list of addresses to search for transactions
        """
        logger.info(f"Processing block: {block_number}")
        block = await self.core.get_block(id_or_num=int(block_number))
        if "transactions" not in block.keys() or not isinstance(block["transactions"], list) \
                or len(block["transactions"]) == 0:
            return
        transactions_hash = await DatabaseController.get_transactions_hash()
        transactions = await asyncio.gather(*[
            self.processing_transaction(data=ProcessingTransaction(
                transaction=block['transactions'][index],
                addresses=addresses,
                timestamp=block["block_header"]["raw_data"]["timestamp"],
                transactionsHash=transactions_hash
            ))
            for index in range(len(block["transactions"]))
        ])
        transactions = list(filter(lambda x: x is not None, transactions))
        if len(transactions) > 0:
            await asyncio.gather(*[
                self.send_to_rabbit(
                    package=transaction,
                    addresses=addresses,
                    transactions_hash=transactions_hash,
                    block_number=block_number
                ) for transaction in transactions
            ])
        return

    async def processing_transaction(self, data: ProcessingTransaction) -> Optional:
        """This method analyzes transactions in detail, and searches for the necessary addresses in them"""
        if data.transaction["ret"][0]["contractRet"] != "SUCCESS":
            return
        token, transaction_addresses = None, []
        transaction_value = data.transaction["raw_data"]["contract"][0]["parameter"]["value"]
        transaction_type = data.transaction["raw_data"]["contract"][0]["type"]
        transaction_hash = data.transaction["txID"]

        sender, recipient = None, None
        if transaction_value.get("owner_address"):
            sender = to_base58check_address(transaction_value.get("owner_address"))
            transaction_addresses.append(sender)
        if transaction_type == "TransferContract" and transaction_value.get("to_address"):
            recipient = to_base58check_address(transaction_value.get("to_address"))
            transaction_addresses.append(recipient)
        elif transaction_type == "TriggerSmartContract":
            pass