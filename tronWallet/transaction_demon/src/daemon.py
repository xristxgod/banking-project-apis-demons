import asyncio
import decimal
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import aiofiles
from tronpy.tron import TAddress
from tronpy.keys import to_base58check_address

from .core import Core
from .utils import Utils
from .external import DatabaseController, CoinController, ElasticController
from config import LAST_BLOCK, decimals, logger


@dataclass()
class ProcessingTransaction:
    transaction: Dict                               # Transaction Data
    addresses: List[TAddress]                       # Wallet addresses in Database
    timestamp: int                                  # Time to send transaction
    transactionsHash: List[str]                     # Transactions in Database


@dataclass()
class SmartContractData:
    amount: decimal.Decimal                         # Transaction amount
    symbol: str                                     # Token name


@dataclass()
class Participant:
    address: TAddress                               # Participant wallet address
    amount: decimal.Decimal                         # Transaction amount


@dataclass()
class Transaction:
    timestamp: int                                  # Time to send transaction
    transactionHash: str                            # Transaction hash/id
    amount: decimal.Decimal                         # Transaction amount
    fee: decimal.Decimal                            # Transaction fee
    inputs: List[Participant]                       # Sender transaction
    outputs: List[Participant]                      # Recipient transaction
    token: Optional[str] = field(default=None)      # Token symbol


@dataclass()
class BodyTransaction:
    address: TAddress                               # Participant transaction in has to db
    transactions: List[Transaction]                 # Transaction list


@dataclass()
class SendTransactionData:
    transactionPackage: BodyTransaction             # Transactions for send
    addresses: List[TAddress]                       # Wallet addresses in Database
    transactionsHash: List[str]                     # Transactions in Database
    blockNumber: int                                # Block in Blockchain


@dataclass()
class Header:
    block: int                                      # Block in Blockchain
    network: str                                    # Example: tron, tron_trc20_usdt, tron_trc20_usdc, etc.


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

    @staticmethod
    async def smart_contract(data: str, address: TAddress) -> Optional[SmartContractData]:
        try:
            coin = CoinController.get_token_by_address(address)
            return SmartContractData(
                amount=decimals.create_decimal(int("0x" + data[72:], 0) / 10 ** coin.decimals),
                symbol=coin.symbol
            )
        except ValueError:
            pass

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
                self.send(data=SendTransactionData(
                    transactionPackage=transaction,
                    addresses=addresses,
                    transactionsHash=transactions_hash,
                    blockNumber=block_number
                ))
                for transaction in transactions
            ])

    async def processing_transaction(self, data: ProcessingTransaction) -> Optional[BodyTransaction]:
        """This method analyzes transactions in detail, and searches for the necessary addresses in them"""
        try:
            if data.transaction["ret"][0]["contractRet"] != "SUCCESS":
                return
            transaction_addresses = []
            transaction_value = data.transaction["raw_data"]["contract"][0]["parameter"]["value"]
            transaction_type = data.transaction["raw_data"]["contract"][0]["type"]
            transaction_hash = data.transaction["txID"]

            sender, recipient = None, None
            if transaction_value.get("owner_address"):
                sender: TAddress = to_base58check_address(transaction_value["owner_address"])
                transaction_addresses.append(sender)
            if transaction_type == "TransferContract" and transaction_value.get("to_address"):
                recipient: TAddress = to_base58check_address(transaction_value["to_address"])
                transaction_addresses.append(recipient)
            elif transaction_type == "TriggerSmartContract" \
                    and CoinController.is_address(transaction_value["contract_address"]) \
                    and 140 > len(transaction_value.get("data", "--")) > 130:
                recipient: TAddress = to_base58check_address("41" + transaction_value["data"][32:72])
                transaction_addresses.append(recipient)

            address: Optional[TAddress] = None
            for transaction_address in transaction_addresses:
                if transaction_address in data.addresses:
                    address = transaction_address
                    break

            if (address is not None) or (transaction_hash in data.transactionsHash):
                token = None
                if address is None:
                    address = sender
                if transaction_type == "TransferContract":
                    amount = "%.8f" % decimals.create_decimal(Utils.from_sun(transaction_value["amount"]))
                elif transaction_type == "TriggerSmartContract":
                    token = await self.smart_contract(
                        data=transaction_value["data"],
                        address=transaction_value["contract_address"]
                    )
                    if token is None:
                        return
                    amount = token.amount
                else:
                    amount = 0

                transaction_fee = await self.core.get_transaction_info(transaction_hash)
                fee = 0 if "fee" not in transaction_fee else \
                    decimals.create_decimal(Utils.from_sun(transaction_fee["fee"]))
                transaction = Transaction(
                    timestamp=data.timestamp,
                    transactionHash=transaction_hash,
                    amount=amount,
                    fee=fee,
                    inputs=[Participant(address=sender, amount=amount)],
                    outputs=[Participant(address=recipient, amount=amount)]
                )
                if token:
                    transaction.token = token
                return BodyTransaction(address=address, transactions=[transaction])
        except Exception as error:
            logger.error(f"{error}")
            await ElasticController.send_exception(ex=error, message="Processing transaction error")

    async def send(self, data: SendTransactionData) -> Optional:
        header_network = (
            f"tron_trc20_{data.transactionPackage.transactions[0].token}"
            if data.transactionPackage.transactions[0].token is not None
            else
            "tron"
        )
        package = [
            Header(block=data.blockNumber, network=header_network),
            data.transactionPackage
        ]
        try:
            pass
        except:
            pass
