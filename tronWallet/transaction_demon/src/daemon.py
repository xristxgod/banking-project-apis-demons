import os
import asyncio
from time import time as timer
from typing import Optional, List

import aiofiles
from tronpy.tron import TAddress
from tronpy.keys import to_base58check_address

from .core import Core
from .utils import Utils, LastBlock, NotSend
from .schemas import (
    ProcessingTransaction, SmartContractData, Participant,
    Transaction, BodyTransaction, SendTransactionData, Header,
    RangeSearch, ListSearch, Start, BalancerMessage
)
from .external import (
    DatabaseController, CoinController, ElasticController,
    MainApp, Balancer, MessageBroker
)
from config import NOT_SEND, Config, decimals, logger


ADMIN_ADDRESSES = [Config.ADMIN_WALLET_ADDRESS, Config.REPORTING_ADDRESS]


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
        last_block = LastBlock.get()
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
            recipient = data.transactionPackage.transactions[0].outputs[0].address
            sender = data.transactionPackage.transactions[0].inputs[0].address

            if sender in ADMIN_ADDRESSES and header_network == "tron" and (recipient in data.addresses):
                """
                If the transaction was made from the admin, and it was not a token transaction, and the recipient
                in this transaction was our address, then the transaction was most likely made to pay the commission.
                """
                package[1].transactions[0].inputs = [Participant(
                    address=Config.REPORTING_ADDRESS,
                    amount=data.transactionPackage.transactions[0].amount + data.transactionPackage.transactions[0].fee
                )]
                package[1].transactions[0].outputs = []
                await MainApp.send(data=package)
            elif sender in ADMIN_ADDRESSES and recipient not in data.addresses:
                """
                If the transaction was sent from the admin address, and the recipient is not our address,
                then most likely these are withdrawal transactions to someone else's wallet.
                """
                if data.transactionPackage.transactions[0].transactionHash in data.transactionsHash:
                    pass

                await MainApp.send(data=package)
            else:
                """
                If the recipient is not an admin wallet, then this transaction is from someone
                else's wallet to our wallet.
                """
                token = data.transactionPackage.transactions[0].token
                await MainApp.send(data=package)
                await Balancer.send(data=BalancerMessage(
                    address=package[1].address,
                    network=token if token is not None else "TRX"
                ))
        except Exception as error:
            logger.error(f"{error}")
            await ElasticController.send_exception(ex=error, message="Send to rabbit error")
            await NotSend.save(data=package)

    @staticmethod
    async def resend() -> Optional:
        """Resend data if data in dir > 0"""
        files = os.listdir(NOT_SEND)
        for file_name in files:
            try:
                path = os.path.join(NOT_SEND, file_name)
                async with aiofiles.open(path, 'r') as file:
                    values = await file.read()
                await MessageBroker.send(values=values)
                os.remove(path)
            except Exception as error:
                logger.error(f"Error: {error}")
                logger.error(f"Not send: {file_name}")
                continue

    async def run(self) -> Optional:
        """Run daemon infinitely"""
        start_block = await self.get_last_block_number()
        pack_size = 1
        while True:
            end_block = await self.get_node_block_number()
            if end_block - start_block < pack_size:
                await asyncio.sleep(3)
            else:
                start_time = timer()
                addresses = await DatabaseController.get_addresses()
                success = await asyncio.gather(*[
                    self.processing_block(block_number=block_number, addresses=addresses)
                    for block_number in range(start_block, start_block + pack_size)
                ])
                logger.info(f"End block: {start_block}. Time taken: {start_time - timer()} sec")
                if all(success):
                    start_block += pack_size
                    await LastBlock.save(number=start_block)
                else:
                    await ElasticController.send_error(message=f"Block {start_block} error!")
                    continue

    async def start_in_range(self, data: RangeSearch) -> Optional:
        logger.info("Start range search")
        for block_number in range(data.startBlock, data.endBlock):
            await self.processing_block(block_number=block_number, addresses=data.addresses)

    async def start_in_list_block(self, data: ListSearch) -> Optional:
        logger.info("Start list search")
        for block_number in data.listBlock:
            await self.processing_block(block_number=int(block_number), addresses=data.addresses)

    async def start(self, data: Optional[Start] = None) -> Optional:
        if data is None:
            await ElasticController.send_message("Start TRON demon")
            await self.run()
        else:
            if data.addresses is None:
                addresses = await DatabaseController.get_addresses()
            else:
                addresses = data.addresses

            if data.listBlock:
                await self.start_in_list_block(data=ListSearch(
                    listBlock=data.listBlock,
                    addresses=addresses
                ))
            elif data.startBlock and data.endBlock is None:
                await self.start_in_range(data=RangeSearch(
                    startBlock=data.startBlock,
                    endBlock=await self.get_node_block_number(),
                    addresses=addresses
                ))
            elif data.startBlock is None and data.endBlock:
                await self.start_in_range(data=RangeSearch(
                    startBlock=await self.get_node_block_number(),
                    endBlock=data.endBlock,
                    addresses=addresses
                ))
            else:
                await self.start_in_range(data=RangeSearch(
                    startBlock=data.startBlock,
                    endBlock=data.endBlock,
                    addresses=addresses
                ))
            logger.info("End search")
