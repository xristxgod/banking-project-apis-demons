import time
import json
from copy import deepcopy
import os
import uuid
from time import time as t
import datetime as dt
from uuid import uuid4
from bit.network.services import NetworkAPI
from config import ERROR, NOT_SEND, LAST_BLOCK, logger, decimal, Decimal, WALLET_FEE_DEFAULT, ADMIN_ADDRESS
from .external_data.database import DB
from .external_data.es_send import send_exception_to_kibana, send_msg_to_kibana
from .external_data.rabbit_mq import RabbitMQ
from .utils import convert_time, get_transaction_in_db
from typing import Optional, List


class FindTransactionsConfig:
    db: DB = DB()
    rabbit: RabbitMQ = RabbitMQ()

    user: str = os.getenv("rpcUser")
    password: str = os.getenv("rpcPass")
    host: str = os.getenv("rpcHost")
    port: int = int(os.getenv("rpcPort"))


class TransactionsDemon(FindTransactionsConfig):
    def __init__(self):
        # Connect to Bitcoin Core Node
        self._node = NetworkAPI.connect_to_node(
            user=self.user, password=self.password,
            host=self.host, port=self.port,
        )

    def _get_block(self) -> int:
        """ Returns the last available block """
        return int(self._node.getblockcount())

    def _get_transactions(self, block=None):
        """ Returns a block with transactions """
        if not block:
            block = self._get_block()
            with open(LAST_BLOCK, 'r') as file:
                # We read from the file if the last block is more than 2, then we take it away,
                # if it has not changed in any way, then we wait.
                last_block = file.read()
            logger.error('START PROCESSING TRANSACTION')
            if last_block:
                last_block = int(last_block)
                # Will wait until a new block appears
                while block - last_block == 0:
                    time.sleep(10)
                    block = self._get_block()
                    logger.error(f'BLOCK: {block} | LAST_BLOCK: {last_block}')
                # If the block has increased by more than one, then go to the next block.
                if block - last_block > 1:
                    block = last_block + 1
            logger.error('END PROCESSING TRANSACTION')
            with open(LAST_BLOCK, 'w') as file:
                # Writing down the last block
                logger.error(f'WRITE TO {LAST_BLOCK} NEW DATA: {block}')
                file.write(str(block))
            with open(LAST_BLOCK, 'r') as file:
                logger.error(f'INSIDE {LAST_BLOCK}: {file.read()}')
        else:
            if block > self._get_block():
                last_block = self._get_block()
                while block != last_block:
                    time.sleep(10)
                    last_block = self._get_block()

        block_hash = self._node.getblockhash(block)
        block_obj = self._node.getblock(block_hash)
        return block_obj["tx"], block, block_obj["time"], convert_time(block_obj["time"])

    def _script(
            self, transactions: list, block: int,
            time_stamp, date_time, db_addresses: Optional[List[str]] = None
    ) -> None:
        """ Transaction search script """

        all_transactions_hash_in_db = DB.get_all_transactions_hash()
        if db_addresses is None:
            addresses = self.db.get_addresses()
        else:
            addresses = db_addresses

        packages_by_addresses = []

        for tx in transactions:
            tx = self._node.getrawtransaction(tx, True)
            senders = self.__get_senders(tx["vin"])
            addresses_from: list = senders[0]
            amount_from: float = senders[1]
            for_pack_senders: list = senders[2]

            recipient = self.__get_recipients(tx["vout"])
            addresses_to: list = recipient[0]
            amount_to: float = recipient[1]
            for_pack_recipient: list = recipient[2]

            fee = round(Decimal(amount_from - amount_to), 8)

            #  Check the presence of such addresses in DB
            address = None
            if any([x in addresses for x in addresses_from]):
                address = addresses_from
            elif any([x in addresses for x in addresses_to]):
                address = addresses_to
            elif any([x == ADMIN_ADDRESS for x in addresses_from]):
                address = [ADMIN_ADDRESS]
            if address is not None:
                packages_by_addresses.extend(
                    self.__packaging_for_dispatch(
                        address=address,
                        tx_id=tx["txid"],
                        from_=for_pack_senders,
                        to_=for_pack_recipient,
                        amount="%.8f" % decimal.create_decimal(repr(amount_from)),
                        fee=fee,
                        time_stamp=time_stamp, date_time=date_time
                    )
                )
            else:
                continue
        if len(packages_by_addresses) > 0:
            for package in packages_by_addresses:
                self.__send_to_rabbit_mq(
                    [{"network": "btc", "block": block}, package],
                    all_transactions_hash_in_db
                )

    def __get_senders(self, vin: list) -> tuple:
        """ Get the input addresses and the sum of the output """
        addresses, amount, full = [], 0, []
        for v in vin:
            try:
                inp = self._node.getrawtransaction(v["txid"], True)
                values = inp["vout"][int(v["vout"])]
                addresses.extend(values["scriptPubKey"]["addresses"])
                amount += values["value"]
                full.append({
                    "address": values["scriptPubKey"]["addresses"][0],
                    "amount": "%.8f" % decimal.create_decimal(repr(values["value"]))
                })
            except Exception:
                continue
        return addresses, amount, full

    def __get_recipients(self, vout: list) -> tuple:
        """ Get output address and amount """
        addresses, amount, full = [], 0, []
        for v in vout:
            try:
                addresses.extend(v["scriptPubKey"]["addresses"])
                amount += v["value"]
                full.append({
                    "address": v["scriptPubKey"]["addresses"][0],
                    "amount": "%.8f" % decimal.create_decimal(repr(v["value"]))
                })
            except Exception:
                continue
        return addresses, amount, full

    def __packaging_for_dispatch(
            self, address: str, tx_id: str,
            from_: list, to_: list, amount: str, fee: str,
            time_stamp, date_time
    ):
        """ Packaging for further sending to RabbitMQ """
        values = {
            "time": time_stamp,
            "datetime": date_time,
            "transactionHash": tx_id,
            "amount": str(amount),
            "fee": str(fee),
            "senders": from_,
            "recipients": to_
        }
        return self.__add_into_addresses(
            address=address, transaction=values,
        )

    def __add_into_addresses(self, address: str, transaction: dict):
        """ Add a transaction to the array for the desired address """
        packages_by_addresses = []
        for index in range(len(packages_by_addresses)):
            if address == packages_by_addresses[index]["address"]:
                packages_by_addresses[index]["transactions"].append(transaction)
                break
        else:
            packages_by_addresses.append({"address": address, "transactions": [transaction]})
        return packages_by_addresses

    # def __edit_dummy_tx_with_fee_after_sending(self, package: List[dict]):
    #     dummy = [
    #         {"network": 'btc', "block": package[0]['block']},
    #         deepcopy(package[1])
    #     ]
    #     dummy[1]['transactions'][0]['transactionHash'] = str(uuid4())
    #     dummy[1]['transactions'][0]['amount'] = dummy[1]['transactions'][0]['fee']
    #     dummy[1]['transactions'][0]['fee'] = '0.00000000'
    #     dummy[1]['transactions'][0]['recipients'] = []
    #     dummy[1]['transactions'][0]['senders'] = [{
    #         'address': WALLET_FEE_DEFAULT,
    #         'amount': dummy[1]['transactions'][0]['amount']
    #     }]
    #     send_msg_to_kibana(msg=f'DUMMY TX WITH FEE AFTER SENDING: {dummy}')
    #     self.rabbit.send_message(json.dumps(dummy))

    def __send_to_rabbit_mq(self, package: list, all_transactions_hash_in_db) -> None:
        """ Send collected data to queue """
        try:
            for index in range(len(package[1]['transactions'])):
                if package[1]["transactions"][index]["transactionHash"] in all_transactions_hash_in_db:
                    package[1]['transactions'][index] = get_transaction_in_db(
                        transaction_hash=package[1]['transactions'][index]["transactionHash"],
                        transaction=package[1]['transactions'][index]
                    )
                    # self.__edit_dummy_tx_with_fee_after_sending(package)
            self.rabbit.send_message(json.dumps(package))
            send_msg_to_kibana(msg=f'NEW TX: {package}')
        except Exception as e:
            send_exception_to_kibana(e, 'SENDING TO MQ ERROR')
            with open(ERROR, 'a', encoding='utf-8') as file:
                # If an error occurred on the RabbitMQ side, write about it.
                file.write(f"Error: {package} | RabbitMQ not responding {e} \n")
            new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
            with open(new_not_send_file, 'w') as file:
                # Write all the verified data to a json file, and do not praise the work
                file.write(str(package))

    def __run(self):
        """ The script runs all the time """
        while True:
            start = t()
            logger.error(f'RUN NEW ITERATION: START = {start}')
            trx, block, time_stamp, date_time = self._get_transactions()
            logger.error("Getting started: {} | Block: {}".format(
                str(dt.datetime.now()).split(".")[0], block
            ))
            self._script(transactions=trx, block=block, time_stamp=time_stamp, date_time=date_time)
            logger.error("End block: {}. Time taken: {} sec".format(
                block, str(dt.timedelta(seconds=int(t() - start)))
            ))

    def __start_in_range(self, start_block, end_block):
        for block_number in range(start_block, end_block):
            addresses = self.db.get_addresses()
            logger.error(f'PROCESSING BLOCK: {block_number}')
            trx, block, time_stamp, date_time = self._get_transactions(block=block_number)
            self._script(
                transactions=trx, block=block, db_addresses=addresses,
                time_stamp=time_stamp, date_time=date_time
            )

    def __send_all_from_folder_not_send(self):
        files = os.listdir(NOT_SEND)
        all_transactions_hash_in_db = DB.get_all_transactions_hash()
        for file_name in files:
            try:
                path = os.path.join(NOT_SEND, file_name)
                with open(path, 'r') as file:
                    values = json.loads(file.read())
                self.__send_to_rabbit_mq(values, all_transactions_hash_in_db)
                os.remove(path)
            except:
                continue

    def start(self, start_block: int = None, end_block: int = None):
        if start_block and end_block:
            self.__start_in_range(start_block, end_block)
        elif start_block and not end_block:
            self.__start_in_range(start_block, self._get_block() + 1)
        elif not start_block and end_block:
            self.__start_in_range(self._get_block(), end_block)
        else:
            send_msg_to_kibana(f'DEMON IS STARTING')
            self.__send_all_from_folder_not_send()
            self.__run()
