import asyncio
import os
import uuid
import json
import datetime as dt
from time import time as timer, sleep
from decimal import Decimal
from typing import List
from web3 import Web3, HTTPProvider, AsyncHTTPProvider
from web3.eth import AsyncEth
from .external_data.database import DB
from .external_data.rabbit_mq import RabbitMQ
from .utils import convert_time
from config import ERROR, NOT_SEND, LAST_BLOCK, logger, NODE_URL, BASE_DIR

ERC20_ABI = json.loads('[{"constant": true, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "success", "type": "bool"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "success", "type": "bool"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [{"name": "", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [], "payable": false, "type": "function"}, {"constant": true, "inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "type": "function"}]')


class TransactionsDemon:
    db: DB = DB()
    rabbit: RabbitMQ = RabbitMQ()
    abi = ERC20_ABI

    def __init__(self):
        self.__node = None
        self.connect()
        self.__contracts = {}
        with open(f'{BASE_DIR}/tokens.txt', 'r') as f:
            rows = f.read().split('\n')
        self.tokens_addresses = [int(x.split('==')[-1], 0) for x in rows]
        sleep(3)

    def connect(self):
        provider: HTTPProvider = HTTPProvider(NODE_URL)
        self.__node = Web3(provider)

    def __get_block_number(self) -> int:
        """Get block number"""
        while True:
            try:
                return int(self.__node.eth.block_number)
            except Exception as e:
                logger.error(e)
                sleep(3)
                self.connect()
                continue

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
                    sleep(0.3)
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
                    sleep(0.3)
                    last_block = self.__get_block_number()

        return self.__node.eth.get_block(int(block))

    async def processing_transactions(self, transactions, addresses, timestamp):
        funded_trx_for_sending = []
        async_provider: AsyncHTTPProvider = AsyncHTTPProvider(NODE_URL)
        async_w3 = Web3(async_provider, modules={'eth': (AsyncEth,)}, middlewares=[])
        for tx_bytes in transactions:
            try:
                tx = dict(await async_w3.eth.get_transaction(async_w3.toHex(tx_bytes)))
            except:
                continue
            try:
                tx_addresses = []
                if tx['from'] is not None:
                    tx_addresses.append(async_w3.toChecksumAddress(tx["from"]))
                if tx['to'] is not None:
                    tx_addresses.append(async_w3.toChecksumAddress(tx["to"]))
            except Exception as e:
                logger.error(f'{e}')
                logger.error(tx)
                continue

            contract_values = await self.processing_smart_contract(async_w3, tx, tx_addresses)

            #  Check the presence of such addresses in DB
            address = None
            for tx_address in tx_addresses:
                if int(tx_address, 0) in addresses:
                    address = tx_address
                    break
            if address is not None:
                receipt = self.__node.eth.wait_for_transaction_receipt(tx["hash"])
                fee = "%.18f" % (self.__node.fromWei(receipt["gasUsed"] * tx["gasPrice"], "ether"))
                values = {
                    "time": str(timestamp),
                    "datetime": str(convert_time(str(timestamp)[:10])),
                    "transactionHash": str(self.__node.toHex(tx["hash"])),
                    "amount": str(self.__node.fromWei(tx["value"], "ether")),
                    "fee": fee,
                    "senders": [tx["from"]],
                    "recipients": [tx["to"]]
                }
                values.update(contract_values)
                funded_trx_for_sending.append(
                    {"address": address, "transactions": [values]}
                )
            else:
                continue
        return funded_trx_for_sending

    async def __script(self, block: dict, addresses: List):
        """Searching for the right transactions"""
        funded_trx_for_sending = []

        if 'transactions' in block.keys() and isinstance(block['transactions'], list):
            count_trx = len(block['transactions'])
        else:
            logger.error(f"Block: {block['number']} is not have transactions!!")
            return
        if count_trx == 0:
            return
        trx_in_splits = await asyncio.gather(*[
            self.processing_transactions(
                block['transactions'][right_border: (right_border + 1)],
                addresses, block['timestamp']
            )
            for right_border in range(count_trx)
        ])
        for tx_split in trx_in_splits:
            funded_trx_for_sending.extend(tx_split)
        if len(funded_trx_for_sending) > 0:
            packing = await self.__packing_before_sending(block['number'], funded_trx_for_sending)
            for package in packing:
                self.__send_to_rabbit_mq(json.dumps(package))

    async def processing_smart_contract(self, async_w3, tx, tx_addresses):
        if len(tx["input"]) > 10:
            smart_contract = await self.__get_smart_contract_info(
                async_w3=async_w3,
                input_=tx["input"],
                contract_address=tx["to"]
            )
            if smart_contract is not None:
                tx_addresses.append(smart_contract["tokenAddress"])
                return {
                    "token": smart_contract['token'],
                    "name": smart_contract['name'],
                    "amount": smart_contract['amount'],
                }
        return {}

    async def __get_smart_contract_info(self, async_w3, input_: str, contract_address: str) -> dict:
        """If the transaction is inside a smart counter, it will look for"""
        try:
            if int(contract_address, 0) not in self.tokens_addresses:
                return None
            if contract_address not in self.__contracts.keys():
                contract_obj = self.__node.eth.contract(
                    address=async_w3.toChecksumAddress(contract_address),
                    abi=self.abi
                )
                self.__contracts.update({contract_address: {
                    "tokenAddress": async_w3.toChecksumAddress("0x" + input_[34:74]),
                    "token": str(contract_obj.functions.symbol().call()),
                    "name": str(contract_obj.functions.name().call()),
                    "decimals": int(contract_obj.functions.decimals().call())
                }})
            contract = self.__contracts[contract_address]
            return {
                "tokenAddress": contract['tokenAddress'],
                "token": contract['token'],
                "name": contract['name'],
                "amount": str(round(Decimal(int("0x" + input_[-64:], 0) / 10 ** contract['decimals'], ), 9))
            }
        except:
            return None

    async def __packing_before_sending(self, block: int, packages: List[dict]):
        """Add a transaction to the array for the desired address"""
        return [
            [
                {
                    "network": f"eth__mainnet__{package['transactions'][0]['token'].lower()}"
                    if "token" in package['transactions'][0].keys()
                    else 'eth',
                    "block": block
                },
                package
            ] for package in packages
        ]

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
            await self.__script(block=block, addresses=addresses, )

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
