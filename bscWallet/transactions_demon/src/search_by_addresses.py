import asyncio
from typing import List
from datetime import datetime
from config import logger
from .demon import TransactionsDemon
from .external_data.database import DB
from .external_data.es_send import send_exception_to_kibana


class AddressesDemon(TransactionsDemon):
    async def processing_block(self, block_number: int, addresses):
        try:
            counter = {a: 0 for a in addresses}
            ints_addresses = [int(a, 0) for a in addresses]
            block = self._node.eth.get_block(block_number, True)

            if 'transactions' in block.keys() and isinstance(block['transactions'], list):
                count_trx = len(block['transactions'])
            else:
                return None
            if count_trx == 0:
                return None
            all_transactions_hash_in_db = await DB.get_all_transactions_hash()
            trx = await asyncio.gather(*[
                self._processing_transaction(
                    tx=block['transactions'][index],
                    addresses=ints_addresses,
                    timestamp=block['timestamp'],
                    all_transactions_hash_in_db=all_transactions_hash_in_db
                )
                for index in range(count_trx)
            ])
            trx = list(filter(lambda x: x is not None, trx))
            if len(trx) > 0:
                await asyncio.gather(*[
                    self._send_to_rabbit_mq(
                        package=tx,
                        addresses=ints_addresses,
                        all_transactions_hash_in_db=all_transactions_hash_in_db,
                        block_number=block_number
                    ) for tx in trx
                ])
                for tx in trx:
                    sender = tx['transactions'][0]['senders'][0]['address']
                    sender_int = int(tx['transactions'][0]['senders'][0]['address'], 0)
                    if sender_int in ints_addresses:
                        counter[sender] += 1
                return counter
        except Exception as e:
            await send_exception_to_kibana(e, 'BLOCK ERROR')
        return None

    async def start(self, start_block: int = None, end_block: int = None, addresses: List[str] = None):
        is_all = False
        if 'all' in addresses:
            is_all = True
            addresses = await self.db.get_addresses_raw()
        last = await self.get_node_block_number() if end_block is None else end_block
        if start_block is None:
            start_block = 1
        addresses = [self._node.toChecksumAddress(a) for a in addresses]
        address_counter = {
            address.lower(): self._node.eth.get_transaction_count(address)
            for address in addresses
        }
        count_all = sum([x for x in address_counter.values()])
        inc_count = 0
        last_count = 0
        for current_block in range(last, start_block - 1, -1):
            filtered_addresses = [a for a, c in address_counter.items() if c > 0]
            if is_all:
                if last_count != inc_count:
                    logger.error(f'{"%.4f" % ((inc_count * 100) / count_all)}% | {inc_count} / {count_all}')
                    last_count = inc_count
            else:
                logger.error(f'{datetime.now()} | BLOCK: {current_block} | COUNT: {address_counter}')
            if len(filtered_addresses) == 0:
                logger.error('FINISH')
                return
            count_sends = await self.processing_block(block_number=current_block, addresses=filtered_addresses)
            if count_sends is None:
                continue
            for key, value in count_sends.items():
                address_counter[key.lower()] -= value
                inc_count += value
