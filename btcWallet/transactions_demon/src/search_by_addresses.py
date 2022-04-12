from typing import List
import requests
from config import logger
from .demon import TransactionsDemon
from .utils import convert_time


class AddressesDemon(TransactionsDemon):
    def start(self, start_block: int = None, end_block: int = None, addresses: List[str] = None):
        if 'all' in addresses:
            addresses = await self.db.get_addresses()
        count_all = len(addresses)
        for index, address in enumerate(addresses):
            try:
                logger.error(f'ADDRESS: {address} ({index+1} / {count_all})')
                transactions = requests.get(
                    f'https://blockchain.info/rawaddr/{address}'
                ).json()['txs']
                for tx in transactions:
                    self._script(
                        transactions=[tx['hash']],
                        block=tx['block_height'],
                        time_stamp=tx['time'],
                        date_time=convert_time(tx["time"]),
                        db_addresses=addresses
                    )
            except Exception as e:
                logger.error(f'ERROR: ({address}) {e}')
