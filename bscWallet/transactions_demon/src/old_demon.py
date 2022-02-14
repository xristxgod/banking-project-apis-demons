import asyncio
import os
import uuid
import json
import datetime as dt
from time import time as timer, sleep
from config import ADMIN_ADDRESS, decimal
from typing import List, Optional
from web3 import Web3, HTTPProvider, AsyncHTTPProvider
from web3.eth import AsyncEth
from .external_data.database import DB
from .external_data.rabbit_mq import RabbitMQ
from .utils import convert_time, get_transaction_in_db
from config import ERROR, NOT_SEND, LAST_BLOCK, logger, NODE_URL
from web3.middleware import geth_poa_middleware


ERC20_ABI = json.loads('[{"constant": true, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "success", "type": "bool"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "success", "type": "bool"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [{"name": "", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [], "payable": false, "type": "function"}, {"constant": true, "inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "type": "function"}]')


class TransactionsDemon:
    db: DB = DB()
    rabbit: RabbitMQ = RabbitMQ()
    abi = ERC20_ABI

    def __init__(self):
        self.__node: Optional[Web3] = None
        self.connect()
        self.__contracts = {}

        for contract in self.db.get_tokens():
            self.__contracts.update({contract[3].lower(): {
                "tokenAddress": self.__node.toChecksumAddress(contract[3]),
                "token": contract[2],
                "name": contract[1],
                "decimals": contract[4]
            }})

        self.tokens_addresses = [int(x, 0) for x in self.__contracts.keys()]
        sleep(3)

    def connect(self):
        provider: HTTPProvider = HTTPProvider(NODE_URL)
        self.__node = Web3(provider)
        if NODE_URL.startswith('https'):
            self.__node.middleware_onion.inject(geth_poa_middleware, layer=0)

    def __get_block_number(self) -> int:
        """Get block number"""
        while True:
            try:
                return int(self.__node.eth.block_number)
            except Exception as e:
                logger.error(e)
                sleep(0.3)
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
                    sleep(0.2)
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
        # else:
        #     last_block = self.__get_block_number()
        #     while block != last_block:
        #         sleep(0.3)
        #         last_block = self.__get_block_number()

        return self.__node.eth.get_block(int(block))

    async def processing_transactions(self, transactions, addresses, timestamp, all_transactions_hash_in_db):
        funded_trx_for_sending = []
        async_provider: AsyncHTTPProvider = AsyncHTTPProvider(NODE_URL)
        async_w3 = Web3(async_provider, modules={'eth': (AsyncEth,)}, middlewares=[])

        for tx_bytes in transactions:
            try:
                tx_hash = async_w3.toHex(tx_bytes)
                if self.__node.eth.get_transaction_receipt(tx_hash) is None:
                    continue
                tx = dict(await async_w3.eth.get_transaction(tx_hash))
            except Exception as e:
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
            contract_values = await self.processing_smart_contract(tx, tx_addresses)

            #  Check the presence of such addresses in DB
            address = None
            for tx_address in tx_addresses:
                if int(tx_address, 0) in addresses:
                    address = tx_address
                    break

            if address is not None or tx_hash in all_transactions_hash_in_db:
                amount = str(self.__node.fromWei(tx["value"], "ether"))
                receipt = self.__node.eth.wait_for_transaction_receipt(tx["hash"])
                fee = "%.18f" % (self.__node.fromWei(receipt["gasUsed"] * tx["gasPrice"], "ether"))
                values = {
                    "time": timestamp,
                    "datetime": str(convert_time(str(timestamp)[:10])),
                    "transactionHash": tx_hash,
                    "amount": amount,
                    "fee": fee,
                    "senders": [{
                        "address": tx['from'],
                        "amount": amount if 'amount' not in contract_values.keys() else contract_values['amount'],
                    }],
                    "recipients": [{
                        "address": tx['to'],
                        "amount": amount,
                    }],
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
        all_transactions_hash_in_db = await DB.get_all_transactions_hash()
        trx_in_splits = await asyncio.gather(*[
            self.processing_transactions(
                block['transactions'][right_border: (right_border + 1)],
                addresses, block['timestamp'], all_transactions_hash_in_db
            )
            for right_border in range(count_trx)
        ])
        for tx_split in trx_in_splits:
            funded_trx_for_sending.extend(tx_split)
        if len(funded_trx_for_sending) > 0:
            packing = await self.__packing_before_sending(block['number'], funded_trx_for_sending)
            for package in packing:
                self.__send_to_rabbit_mq(package, addresses, all_transactions_hash_in_db)

    async def processing_smart_contract(self, tx, tx_addresses):
        if len(tx["input"]) > 64:
            smart_contract = await self.__get_smart_contract_info(
                input_=tx["input"],
                contract_address=tx["to"]
            )
            if smart_contract is not None:
                tx_addresses.append(smart_contract["toAddress"])
                return {
                    "token": smart_contract['token'],
                    "name": smart_contract['name'],
                    "amount": smart_contract['amount'],
                    "recipients": [{
                        "address": smart_contract['toAddress'],
                        "amount": smart_contract['amount'],
                    }]
                }
        return {}

    async def __get_smart_contract_info(self, input_: str, contract_address: str) -> dict:
        """If the transaction is inside a smart counter, it will look for"""
        try:
            if contract_address is None:
                return None
            contract_address: str = contract_address.lower()
            if int(contract_address, 0) not in self.tokens_addresses:
                return None
            amount = input_[-64:]
            to_address = f'0x{input_[-104:-64]}'

            contract = self.__contracts[contract_address]
            format_str = f"%.{contract['decimals']}f"
            return {
                "tokenAddress": contract['tokenAddress'],
                "token": contract['token'],
                "name": contract['name'],
                "toAddress": to_address,
                "amount": format_str % (decimal.create_decimal(int("0x" + amount, 0)) / 10 ** contract['decimals'])
            }
        except Exception as e:
            logger.error(f'ERROR GET CONTRACT: {e}. CONTRACT ADDRESS: {contract_address} | {self.__contracts}')
            return None

    async def __packing_before_sending(self, block: int, packages: List[dict]):
        """Add a transaction to the array for the desired address"""
        return [
            [
                {
                    "network": f"bsc_bip20_{package['transactions'][0]['token'].lower()}"
                               if "token" in package['transactions'][0].keys()
                               else 'bnb',
                    "block": block
                },
                package
            ] for package in packages
        ]

    def send_message_tx_from_admin_address(self, package: List[dict]):
        package[1]['transactions'][0]['recipients'] = []
        self.rabbit.send_founded_message(package)

    def __send_to_rabbit_mq(self, package, addresses, all_transactions_hash_in_db) -> None:
        """Send collected data to queue"""
        try:
            package[1]['transactions'][0]['recipients'][0]['address'] = package[1]['transactions'][0]['recipients'][0]['address'].lower()
            package[1]['transactions'][0]['senders'][0]['address'] = package[1]['transactions'][0]['senders'][0]['address'].lower()
            package[1]['address'] = package[1]['address'].lower()

            recipient = int(package[1]['transactions'][0]['recipients'][0]['address'], 0)
            sender = int(package[1]['transactions'][0]['senders'][0]['address'], 0)
            admin = int(ADMIN_ADDRESS, 0)

            token = (
                package[1]['transactions'][0]['token']
                if 'token' in package[1]['transactions'][0].keys()
                else None
            )
            if (sender == admin) and (token is None) and (recipient in addresses):
                logger.error(f'RECIEVED FEE FOR SENDING TOKEN')
                # If it's sending fee for transfer tokens to main wallet between main wallet and one of our wallets
                self.rabbit.got_fee_for_sending_token_to_main_wallet(
                    package[1]['transactions'][0]['recipients'][0]['address']
                )
                self.send_message_tx_from_admin_address(package)
            elif (sender == admin) and (recipient not in addresses):
                logger.error(f'SENDING FROM MAIN WALLET')
                if package[1]["transactions"][0]["transactionHash"] in all_transactions_hash_in_db:
                    txn = await get_transaction_in_db(
                        transaction_hash=package[1]['transactions'][0]["transactionHash"],
                        transaction=package[1]['transactions'][0]
                    )
                    package[1]['transactions'][0] = txn
                self.rabbit.send_founded_message(package)
            elif recipient != admin:
                # If it's not sending to main wallet
                self.rabbit.send_founded_message(package)
                self.rabbit.request_for_sending_to_main_wallet(
                    token=token,
                    address=package[1]['transactions'][0]['recipients'][0]['address']
                )
        except Exception as e:
            logger.error(f'SENDING TO MQ ERROR: {e} | {package}')
            with open(ERROR, 'a', encoding='utf-8') as file:
                # If an error occurred on the RabbitMQ side, write about it.
                file.write(f"Error: {package} | RabbitMQ not responding {e} \n")
            new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
            with open(new_not_send_file, 'w') as file:
                # Write all the verified data to a json file, and do not praise the work
                file.write(json.dumps(package))

    async def __run(self):
        """ The script runs all the time """
        while True:
            start = timer()
            logger.error(f'RUN NEW ITERATION: START = {start}')
            block = self.__get_block_info()

            logger.error("Getting started: {} | Block: {}".format(
                str(dt.datetime.now()).split(".")[0], block['number']
            ))

            addresses = await self.db.get_addresses()
            await self.__script(block=block, addresses=addresses,)

            logger.error("End block: {}. Time taken: {} sec".format(
                block['number'], str(dt.timedelta(seconds=int(timer() - start)))
            ))

    async def __start_in_range(self, start_block, end_block):
        for block_number in range(start_block, end_block):
            addresses = await self.db.get_addresses()
            logger.error(f'PROCESSING BLOCK: {block_number}')
            block = self.__get_block_info(block=block_number)
            await self.__script(block=block, addresses=addresses)

    def __send_all_from_folder_not_send(self):
        files = os.listdir(NOT_SEND)
        addresses = await self.db.get_addresses()
        all_transactions_hash_in_db = await DB.get_all_transactions_hash()

        for file_name in files:
            try:
                path = os.path.join(NOT_SEND, file_name)
                with open(path, 'r') as file:
                    values = json.loads(file.read())
                self.__send_to_rabbit_mq(values, addresses, all_transactions_hash_in_db)
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
