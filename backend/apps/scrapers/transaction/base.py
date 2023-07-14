import abc
import asyncio
from typing import Mapping
from dataclasses import dataclass

from apps.scrapers.queue import Queue
from apps.orders.models import OrderStatus, Payment, TempWallet


@dataclass()
class Message:
    transaction_hash: str
    timestamp: int
    sender: str
    contract_address: str
    amount: int
    fee: int
    order_id: int


class AbstractTransactionScraper(metaclass=abc.ABCMeta):
    queue = Queue()

    @classmethod
    async def get_orders(cls) -> dict[str: int]:
        values = TempWallet.objects.filter(
            payment__order__status__in=[OrderStatus.CREATED, OrderStatus.SENT],
            payment__type=Payment.DEPOSIT_TYPES,
        ).values_list(
            'pk', 'address', 'payment__order__currency',
            'payment__order__amount',
            flat=True
        )

        return {
            address: {
                'pk': pk,
                'currency': currency,
                'amount': amount,
            }
            for pk, address, currency, amount in values
        }

    async def send_to_queue(self, message) -> bool:
        pass

    async def parsing_block(self, block_number: int, orders: dict[str: int]):
        raw_transactions, extra = await self.get_block_detail(block_number)

        if not raw_transactions:
            return True

        result = await asyncio.gather(*[
            self.parsing_transaction(raw_transaction, orders, extra)
            for raw_transaction in raw_transactions
        ])

        if messages := list(filter(lambda x: x is not None, result)):
            result = await asyncio.gather(*[
                self.send_to_queue(message)
                for message in messages
            ])
            return all(result)

        return True

    async def run(self):
        pass

    async def run_with_range_block(self, start: int, end: int):
        pass

    async def run_with_list_blocks(self, list_blocks: list[int]):
        pass

    async def __call__(self, **params):
        if params['start'] or params['end']:
            return await self.run_with_range_block(
                start=params['start'] or await self.get_latest_block_number(),
                end=params['end'] or await self.get_latest_block_number(),
            )
        elif params['list_blocks']:
            return await self.run_with_list_blocks(
                list_blocks=sorted(params['list_blocks']),
            )
        else:
            return await self.run()

    @abc.abstractmethod
    async def get_latest_block_number(self) -> int: ...

    @abc.abstractmethod
    async def get_block_detail(self, block_number: int) -> tuple: ...

    @abc.abstractmethod
    async def parsing_transaction(self, transaction: Mapping, orders: dict[str: int], extra: dict): ...
