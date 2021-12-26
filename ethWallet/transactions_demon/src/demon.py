import asyncio
import math
import os
import uuid
import time
import json
import datetime as dt
from time import time as timer
from decimal import Decimal
from typing import List, Optional
import web3.exceptions
from web3 import Web3, HTTPProvider, AsyncHTTPProvider
from web3.eth import AsyncEth
from .external_data.database import DB
from .external_data.rabbit_mq import RabbitMQ
from .utils import convert_time
from config import ERROR, NOT_SEND, LAST_BLOCK, logger


ERC20_ABI = json.loads('[{"constant": true, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "success", "type": "bool"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "success", "type": "bool"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [{"name": "", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [], "payable": false, "type": "function"}, {"constant": true, "inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "type": "function"}]')


class TransactionsDemonConfig:
    db: DB = DB()
    rabbit: RabbitMQ = RabbitMQ()
    provider: HTTPProvider = HTTPProvider(
        os.environ.get("NodeURL", 'https://mainnet.infura.io/v3/2a8e1d2dafe9470d8eb6c6a115a45d17')
    )
    abi = ERC20_ABI


class TransactionsDemon(TransactionsDemonConfig):
    def __init__(self):
        self.__node = Web3(self.provider)

    def __get_block_number(self) -> int:
        """Get block number"""
        return int(self.__node.eth.block_number)

    def __get_block_info(self, block: int = None):
        """Returns a block with transaction"""
        if not block:
            block = self.__get_block_number()
            with open(LAST_BLOCK, "r") as file:
                # We read from the file if the last block is more than 2, then we take it away,
                # if it has not changed in any way, then we wait.
                last_block = file.read()
            logger.error("START PROCESSING TRANSACTION")
            if last_block:
                last_block = int(last_block)
                # Will wait until a new block appears
                while block == last_block:
                    time.sleep(2)
                    block = self.__get_block_number()
                    logger.error(f"BLOCK: {block} | LAST_BLOCK: {last_block}")
                # If the block has increased by more than zero, then go to the next block.
                if block - last_block > 0:
                    block = last_block + 1
            logger.error("END PROCESSING TRANSACTION")
            with open(LAST_BLOCK, "w") as file:
                # Writing down the last block
                logger.error(f"WRITE TO {LAST_BLOCK} NEW DATA {block}")
                file.write(str(block))
        else:
            if block > self.__get_block_number():
                last_block = self.__get_block_number()
                while block != last_block:
                    time.sleep(2)
                    last_block = self.__get_block_number()

        return self.__node.eth.get_block(int(block))

    async def processing_transactions(self, transactions, addresses, timestamp):
        funded_trx_for_sending = []
        async_provider: AsyncHTTPProvider = AsyncHTTPProvider(
            os.environ.get("NodeURL", 'https://mainnet.infura.io/v3/2a8e1d2dafe9470d8eb6c6a115a45d17')
        )
        async_w3 = Web3(async_provider, modules={'eth': (AsyncEth,)}, middlewares=[])
        for tx_bytes in transactions:
            tx = dict(await async_w3.eth.get_transaction(async_w3.toHex(tx_bytes)))
            try:
                tx_addresses = []
                if tx['from'] is not None:
                    tx_addresses.append(async_w3.toChecksumAddress(tx["from"]))
                if tx['to'] is not None:
                    tx_addresses.append(async_w3.toChecksumAddress(tx["to"]))
            except Exception as e:
                logger.error(f'{e}')
                logger.error(tx)
                raise e
            if 10 < len(tx["input"]) < 160:
                try:
                    smart_contract: dict = await self.__smart_contract_transaction(
                        async_w3=async_w3,
                        input_=tx["input"],
                        contract_address=tx["to"]
                    )
                    tx_addresses.append(smart_contract["toAddress"])
                except Exception:
                    smart_contract = tx["input"]
            elif len(tx["input"]) < 10:
                smart_contract = {}
            else:
                smart_contract = tx["input"]

            #  Check the presence of such addresses in DB
            address = None
            for tx_address in tx_addresses:
                if int(tx_address, 0) in addresses:
                    address = tx_address
                    break
            if address is not None:
                funded_trx_for_sending.extend(self.__packaging_for_dispatch(
                    address=address,
                    trx=tx,
                    smart_contract=smart_contract,
                    block_time=timestamp,
                    funded_trx_for_sending=funded_trx_for_sending
                ))
            else:
                continue
        return funded_trx_for_sending

    async def __script(self, block: dict, addresses: List):
        """Searching for the right transactions"""
        funded_trx_for_sending = []

        if 'transactions' in block.keys() and isinstance(block['transactions'], list):
            count_trx = len(block['transactions'])
        else:
            return

        if count_trx > 15:
            in_split = 7
            trx_in_splits = await asyncio.gather(*[
                self.processing_transactions(
                    block['transactions'][right_border * in_split: (right_border + 1) * in_split],
                    addresses, block['timestamp']
                )
                for right_border in range(0, math.ceil(count_trx / in_split))
            ])
            for tx_split in trx_in_splits:
                funded_trx_for_sending.extend(tx_split)
        else:
            funded_trx_for_sending = await self.processing_transactions(
                block['transactions'],
                addresses, block['timestamp']
            )
        if len(funded_trx_for_sending) > 0:
            for package in funded_trx_for_sending:
                self.__send_to_rabbit_mq(json.dumps([
                    {"network": "eth", "block": block['number']},
                    package
                ]))

    async def __smart_contract_transaction(self, async_w3, input_: str, contract_address: str) -> dict:
        """If the transaction is inside a smart counter, it will look for"""
        try:
            contract = async_w3.eth.contract(
                address=async_w3.toChecksumAddress(contract_address),
                abi=self.abi
            )
            return {
                "toAddress": async_w3.toChecksumAddress("0x" + input_[34:74]),
                "token": str(contract.functions.symbol().call()),
                "amount": str(round(Decimal(int("0x" + input_[122:], 0) / 10 ** int(contract.functions.decimals().call()), ), 9))
            }
        except web3.exceptions.ABIFunctionNotFound:
            return {}
        except Exception:
            return {}

    def __packaging_for_dispatch(
            self, address: str,
            trx: dict,
            smart_contract: dict,
            block_time: int,
            funded_trx_for_sending: List
    ):
        """Packaging for further sending to RabbitMQ"""
        values = {
            "time": str(block_time),
            "datetime": str(convert_time(str(block_time)[:10])),
            "transactionHash": str(self.__node.toHex(trx["hash"])),
            "amount": str(self.__node.fromWei(trx["value"], "ether")),
            "fee": str(self.__node.fromWei(trx["gas"] * trx["gasPrice"], "ether")),
            "senders": trx["from"],
            "recipients": trx["to"],
            "smartContract": smart_contract
        }
        return self.__add_into_addresses(
            address=address, transaction=values, funded_trx_for_sending=funded_trx_for_sending
        )

    def __add_into_addresses(self, address: str, transaction: dict, funded_trx_for_sending: List):
        """Add a transaction to the array for the desired address"""
        for addresses in funded_trx_for_sending:
            if address == addresses["address"]:
                addresses["transactions"].append(transaction)
                break
        else:
            funded_trx_for_sending.append({"address": address, "transactions": [transaction]})
        return funded_trx_for_sending

    def __send_to_rabbit_mq(self, values: list) -> None:
        """Send collected data to queue"""
        try:
            self.rabbit.send_message(values)
        except Exception as e:
            logger.error(f'SENDING TO MQ ERROR: {e}')
            with open(ERROR, 'a', encoding='utf-8') as file:
                # If an error occurred on the RabbitMQ side, write about it.
                file.write(f"Error: {values} | RabbitMQ not responding {e} \n")
            new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
            with open(new_not_send_file, 'w') as file:
                # Write all the verified data to a json file, and do not praise the work
                file.write(str(values))

    async def __run(self):
        """ The script runs all the time """
        while True:
            start = timer()
            logger.error(f'RUN NEW ITERATION: START = {start}')
            block = self.__get_block_info()

            logger.error("Getting started: {} | Block: {}".format(
                str(dt.datetime.now()).split(".")[0], block['number']
            ))

            addresses = self.db.get_addresses()
            await self.__script(block=block, addresses=addresses,)

            logger.error("End block: {}. Time taken: {} sec".format(
                block['number'], str(dt.timedelta(seconds=int(timer() - start)))
            ))

    async def __start_in_range(self, start_block, end_block):
        for block_number in range(start_block, end_block):
            addresses = self.db.get_addresses()
            logger.error(f'PROCESSING BLOCK: {block_number}')
            block = self.__get_block_info(block=block_number)
            await self.__script(block=block, addresses=addresses)

    def __send_all_from_folder_not_send(self):
        files = os.listdir(NOT_SEND)
        for file_name in files:
            try:
                path = os.path.join(NOT_SEND, file_name)
                with open(path, 'r') as file:
                    values = file.read()
                self.__send_to_rabbit_mq(values)
                os.remove(path)
            except:
                continue

    async def start(self, start_block: int = None, end_block: int = None):
        if start_block and end_block:
            await self.__start_in_range(start_block, end_block)
        elif start_block and not end_block:
            await self.__start_in_range(start_block, self.__get_block_number() + 1)
        elif not start_block and end_block:
            await self.__start_in_range(self.__get_block_number(), end_block)
        else:
            self.__send_all_from_folder_not_send()
            await self.__run()
