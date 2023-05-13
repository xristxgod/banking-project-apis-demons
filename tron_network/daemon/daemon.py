import asyncio
import logging
from typing import Optional

import aioredis
from tronpy.tron import TAddress
from tronpy.keys import to_base58check_address

import settings
from core.crypto.node import Node
from apps.transaction.schemas import TransactionType


class BlockController:

    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.client = aioredis.from_url(redis_url)

    def __str__(self):
        return 'daemon_block'

    async def get(self) -> int:
        return await self.client.get(self)

    async def save(self, number: int):
        await self.client.sadd(self, number)


class TransactionDaemon:
    find_type = [
        'TransferContract',
        'TriggerSmartContract',
        'FreezeBalanceV2Contract',
        'UnfreezeBalanceV2Contract',
        'DelegateResourceContract',
        'UnDelegateResourceContract',
    ]

    find_smart_contract_type = {
        'a9059cbb': TransactionType.TRANSFER,
        '095ea7b3': TransactionType.APPROVE,
        '23b872dd': TransactionType.TRANSFER_FROM,
    }

    @classmethod
    def _get_logger(cls) -> logging.Logger:
        pass

    def __init__(self, node: Node, **kwargs):
        self.node = node
        self.addresses = kwargs['addresses']
        self.block_controller = BlockController(redis_url=kwargs.get('redis_url'))

        self.logger = kwargs.get('logger') or self._get_logger()

    async def __call__(self, is_always: bool = True, **kwargs):
        if not is_always:
            return await self.start_in_range(**kwargs)

        start = await self.block_controller.get()
        while True:
            end = await self.node.client.get_latest_block_number()

            if end - start < 1:
                await asyncio.sleep(3)
                continue

            addresses = await self.addresses.all()

            success = await asyncio.gather(*[
                self.parsing_block(
                    number=start,
                    addresses=addresses,
                )
            ])
            self.logger.info(f'Block: start')

            if all(success):
                self.logger.info(f'Block: {start} :: Success')
                start += 1
                await self.block_controller.save(start)
            else:
                self.logger.error(f'Block: {start} :: Error')

    async def start_in_range(self, start: Optional[int] = None, end: Optional[int] = None, **kwargs):
        # TODO
        pass

    async def parsing_block(self, number: int, addresses: list[TAddress]) -> bool:
        block = await self.node.client.get_block(number)

        if len(block.get('transactions', [])) == 0:
            return True

        success = await asyncio.gather(*[
            self.parsing_transaction(
                transaction=transaction,
                addresses=addresses,
            )
            for transaction in block['transaction']
        ])

        return all(success)

    async def _get_addresses_in_data(self, data: str) -> list[TAddress]:
        smart_contract_type = self.find_smart_contract_type.get(data[:8])

        match smart_contract_type:
            case TransactionType.TRANSFER:
                return [to_base58check_address(f'41{data[32:72]}')]
            case TransactionType.APPROVE:
                # TODO
                pass
            case TransactionType.TRANSFER_FROM:
                # TODO
                pass
            case _:
                return []

    async def _get_addresses_in_transaction(self, transaction_value: dict) -> list[TAddress]:
        if transaction_value.get('to_address'):
            return [transaction_value['to_address']]
        elif transaction_value.get('receiver_address'):
            return [transaction_value['receiver_address']]
        else:
            return await self._get_addresses_in_data(transaction_value['data'])

    async def parsing_transaction(self, transaction: dict, addresses: list[TAddress]) -> bool:
        if transaction["ret"][0]["contractRet"] != "SUCCESS":
            return True

        if transaction["raw_data"]["contract"][0]["type"] not in self.find_type:
            return True

        transaction_value = transaction["raw_data"]["contract"][0]["parameter"]["value"]
        addresses_in_transaction = (
            transaction_value["owner_address"],
            *self._get_addresses_in_transaction(transaction_value),
        )

        valid_transaction = False
        for address in addresses_in_transaction:
            if address in addresses:
                valid_transaction = True
                break

        return await self.set_tasks(transaction) if valid_transaction else True

    async def set_tasks(self, transaction: dict) -> bool:
        # TODO send to balancer
        # TODO send to parser
        pass
