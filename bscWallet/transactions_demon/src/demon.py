import asyncio
import os
import aiohttp
import uuid
import json
import datetime as dt
import aiofiles
from time import time as timer, sleep
from config import ADMIN_ADDRESS, decimal
from typing import List, Optional
from web3 import Web3, HTTPProvider
from .external_data.database import DB
from .external_data.rabbit_mq import RabbitMQ
from .utils import convert_time, get_transaction_in_db
from config import ERROR, NOT_SEND, LAST_BLOCK, logger, NODE_URL
from web3.middleware import geth_poa_middleware

INT_ADMIN_ADDRESS = int(ADMIN_ADDRESS, 0)

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

        self.__tokens_addresses = [int(x, 0) for x in self.__contracts.keys()]
        sleep(3)

    def connect(self):
        provider: HTTPProvider = HTTPProvider(NODE_URL)
        self.__node = Web3(provider)
        if NODE_URL.startswith('https'):
            self.__node.middleware_onion.inject(geth_poa_middleware, layer=0)

    async def __rpc_request(self, method: str, *params):
        async with aiohttp.ClientSession(headers={'Content-Type': 'application/json'}) as session:
            async with session.post(
                NODE_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": 1
                },
            ) as resp:
                data = await resp.json()
        return data['result']

    async def __get_block_by_number(self, number: int):
        return self.__node.eth.get_block(number)

    async def __get_smart_contract_info(self, input_: str, contract_address: str) -> dict:
        try:
            if contract_address is None:
                return None
            contract_address: str = contract_address.lower()
            if int(contract_address, 0) not in self.__tokens_addresses:
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

    async def __processing_smart_contract(self, tx, tx_addresses):
        if len(tx["input"]) > 64:
            input_ = tx["input"]
            contract_address = tx["to"]
            if contract_address is None:
                return {}
            contract_address: str = contract_address.lower()
            if int(contract_address, 0) not in self.__tokens_addresses:
                return {}
            amount = input_[-64:]
            to_address = f'0x{input_[-104:-64]}'.lower()

            contract = self.__contracts[contract_address]
            format_str = f"%.{contract['decimals']}f"

            tx_addresses.append(to_address)
            format_amount = format_str % (decimal.create_decimal(int("0x" + amount, 0)) / 10 ** contract['decimals'])
            return {
                "token": contract['token'],
                "name": contract['name'],
                "amount": format_amount,
                "recipients": [{
                    "address": to_address,
                    "amount": format_amount,
                }]
            }
        return {}

    async def __processing_transaction(self, tx, addresses, timestamp, all_transactions_hash_in_db):
        try:
            tx_hash = tx['hash'].hex()
            tx_addresses = []
            tx_from = None
            tx_to = None
            if tx['from'] is not None:
                tx_from = tx['from'].lower()
                tx_addresses.append(self.__node.toChecksumAddress(tx_from))
            if tx['to'] is not None:
                tx_to = tx['to'].lower()
                tx_addresses.append(self.__node.toChecksumAddress(tx_to))

            contract_values = await self.__processing_smart_contract(tx, tx_addresses)

            address = None

            for tx_address in tx_addresses:
                if int(tx_address, 0) in addresses:
                    address = tx_address
                    break

            if address is not None or tx_hash in all_transactions_hash_in_db:
                receipt = await self.__rpc_request('eth_getTransactionReceipt', tx_hash)

                if receipt is None or receipt['status'] == '0x0':
                    return None

                if address is None:
                    address = tx_from

                amount = str(self.__node.fromWei(tx["value"], "ether"))
                fee = "%.18f" % (self.__node.fromWei(int(receipt["gasUsed"], 0) * tx["gasPrice"], "ether"))
                values = {
                    "time": timestamp,
                    "datetime": str(convert_time(str(timestamp)[:10])),
                    "transactionHash": tx_hash,
                    "amount": amount,
                    "fee": fee,
                    "senders": [{
                        "address": tx_from,
                        "amount": amount if 'amount' not in contract_values.keys() else contract_values['amount'],
                    }],
                    "recipients": [{
                        "address": tx_to,
                        "amount": amount,
                    }],
                }
                values.update(contract_values)
                return {"address": address, "transactions": [values]}
            return None
        except Exception as e:
            logger.error(f'PROC TX ERROR: {e} | {tx["from"]} | {tx["to"]}')
            return None

    async def __processing_block(self, block_number: int, addresses):
        try:
            start = timer()
            logger.error(f'RUN NEW ITERATION: {str(dt.datetime.now()).split(".")[0]} | Block: {block_number}')

            block = self.__node.eth.get_block(block_number, True)

            if 'transactions' in block.keys() and isinstance(block['transactions'], list):
                count_trx = len(block['transactions'])
            else:
                return True
            if count_trx == 0:
                return True
            all_transactions_hash_in_db = await DB.get_all_transactions_hash()
            trx = await asyncio.gather(*[
                self.__processing_transaction(
                    tx=block['transactions'][index],
                    addresses=addresses,
                    timestamp=block['timestamp'],
                    all_transactions_hash_in_db=all_transactions_hash_in_db
                )
                for index in range(count_trx)
            ])
            trx = list(filter(lambda x: x is not None, trx))

            if len(trx) > 0:
                await asyncio.gather(*[
                    self.__send_to_rabbit_mq(
                        package=tx,
                        addresses=addresses,
                        all_transactions_hash_in_db=all_transactions_hash_in_db,
                        block_number=block_number
                    ) for tx in trx
                ])
            logger.error(f"END BLOCK: {block_number}. Time: {dt.timedelta(seconds=int(timer() - start))} sec")
            return True
        except Exception as e:
            logger.error(f'BLOCK ERROR: {e}')
            return False

    def __send_message_tx_from_admin_address(self, package: List[dict]):
        package[1]['transactions'][0]['recipients'] = []
        self.rabbit.send_founded_message(package)

    async def __send_to_rabbit_mq(self, package, addresses, all_transactions_hash_in_db, block_number) -> None:
        """Send collected data to queue"""
        token = (
            package['transactions'][0]['token'].lower()
            if 'token' in package['transactions'][0].keys()
            else None
        )
        package_for_sending = [
            {
                "network": f"bsc_bip20_{token}" if token is not None else 'bnb',
                "block": block_number
            },
            package
        ]
        try:
            recipient = package['transactions'][0]['recipients'][0]['address']
            recipient_int = int(recipient, 0)

            sender = package['transactions'][0]['senders'][0]['address']
            sender_int = int(sender, 0)

            if (sender_int == INT_ADMIN_ADDRESS) and (token is None) and (recipient_int in addresses):
                logger.error(f'RECIEVED FEE FOR SENDING TOKEN')
                # If it's sending fee for transfer tokens to main wallet between main wallet and one of our wallets
                self.rabbit.got_fee_for_sending_token_to_main_wallet(recipient)
                self.__send_message_tx_from_admin_address(package_for_sending)
            elif (sender_int == INT_ADMIN_ADDRESS) and (recipient_int not in addresses):
                logger.error(f'SENDING FROM MAIN WALLET')
                tx_hash = package["transactions"][0]["transactionHash"]
                if tx_hash in all_transactions_hash_in_db:
                    package_for_sending[1]['transactions'][0] = await get_transaction_in_db(
                        transaction_hash=tx_hash,
                        transaction=package['transactions'][0]
                    )
                self.rabbit.send_founded_message(package_for_sending)
            elif recipient_int != INT_ADMIN_ADDRESS:
                # If it's not sending to main wallet
                self.rabbit.send_founded_message(package_for_sending)
                self.rabbit.request_for_sending_to_main_wallet(token=token, address=recipient)
        except Exception as e:
            logger.error(f'SENDING TO MQ ERROR: {e} | {package_for_sending}')
            async with aiofiles.open(ERROR, 'a', encoding='utf-8') as file:
                # If an error occurred on the RabbitMQ side, write about it.
                await file.write(f"Error: {package_for_sending} | RabbitMQ not responding {e} \n")
            new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
            async with aiofiles.open(new_not_send_file, 'w') as file:
                # Write all the verified data to a json file, and do not praise the work
                await file.write(json.dumps(package_for_sending))

    async def get_node_block_number(self):
        return int(self.__node.eth.block_number)

    async def __get_last_block_number(self):
        async with aiofiles.open(LAST_BLOCK, "r") as file:
            current_block = await file.read()
        if current_block:
            return int(current_block)
        else:
            return await self.get_node_block_number()

    @staticmethod
    async def __save_block_number(block_number: int):
        async with aiofiles.open(LAST_BLOCK, "w") as file:
            await file.write(str(block_number))

    async def __run(self):
        """ The script runs all the time """
        start = await self.__get_last_block_number()
        pack_size = 1
        while True:
            end = await self.get_node_block_number()
            if end - start < pack_size:
                logger.error('WAIT 3 sec.')
                await asyncio.sleep(3)
            else:
                addresses = await self.db.get_addresses()
                success = await asyncio.gather(*[
                    self.__processing_block(block_number=block_number, addresses=addresses)
                    for block_number in range(start, start + pack_size)
                ])
                if all(success):
                    start += pack_size
                    await self.__save_block_number(start)
                else:
                    logger.error(f'BLOCK ERROR. RUN BLOCK AGAIN')
                    continue

    async def __start_in_range(self, start_block, end_block):
        for block_number in range(start_block, end_block):
            addresses = await self.db.get_addresses()
            logger.error(f'PROCESSING BLOCK: {block_number}')
            await self.__processing_block(block_number=block_number, addresses=addresses)

    async def __send_all_from_folder_not_send(self):
        files = os.listdir(NOT_SEND)
        addresses = await self.db.get_addresses()
        all_transactions_hash_in_db = await DB.get_all_transactions_hash()

        for file_name in files:
            try:
                path = os.path.join(NOT_SEND, file_name)
                with open(path, 'r') as file:
                    values = json.loads(file.read())
                block = values[0]['block']
                await self.__send_to_rabbit_mq(values, addresses, all_transactions_hash_in_db, block)
                os.remove(path)
            except:
                continue

    async def start(self, start_block: int = None, end_block: int = None):
        if start_block and end_block:
            await self.__start_in_range(start_block, end_block)
        elif start_block and not end_block:
            await self.__start_in_range(start_block, await self.get_node_block_number() + 1)
        elif not start_block and end_block:
            await self.__start_in_range(await self.get_node_block_number(), end_block)
        else:
            await self.__send_all_from_folder_not_send()
            await self.__run()
