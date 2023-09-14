import abc
import asyncio
import decimal
import json
from typing import Optional, Self
from dataclasses import dataclass, asdict

from config import celery_app
from core.blockchain.gates import get_node
from core.blockchain.storages import BlockNumberStorage
from core.blockchain.dao import StableCoinDAO, OrderProviderDAO
from core.blockchain.models import Network, StableCoin, OrderProvider


@dataclass()
class Participant:
    address: str
    amount: decimal.Decimal


@dataclass()
class Message:
    timestamp: int
    order_id: int
    network_id: Network.id
    transaction_id: str
    fee: decimal.Decimal
    commission_detail: dict
    amount: decimal.Decimal
    inputs: list[Participant]
    outputs: list[Participant]
    currency_id: Optional[StableCoin.id] = None

    @classmethod
    def from_json(cls, raw_message: dict) -> Self:
        return cls(**raw_message)

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


class AbstractTransactionScraper(metaclass=abc.ABCMeta):
    use_stable_coins: bool = True
    use_order_providers: bool = True

    block_pack_size: int = 1
    dependency_update_interval_by_blocks: int = 100         # every 10 blocks
    sleep_after_new_block = 1                               # 1 sec

    task_path = 'core.blockchain.tasks.parsing_daemons_messages_task'

    def __init__(self, network: Network):
        self.node = get_node(network=network)
        self.storage = BlockNumberStorage(storage_name=str(self))

        self.stable_coins: dict[str: int] = {}
        self.order_providers: list[str] = []

        self.logger = self._get_logger()

    def _get_logger(self):
        from config import get_logger
        return get_logger(name=str(self))

    def __str__(self):
        return f'scraper:{self.node.network.name}'

    __repr__ = __str__

    async def update_stable_coins(self):
        if self.use_stable_coins:
            stable_coins: list[StableCoin] = await StableCoinDAO.filter(filters=[
                StableCoin.network_id == self.node.network.id,
                ])
            self.stable_coins = {
                stable_coin.address: stable_coin.decimal_place
                for stable_coin in stable_coins
            }

    async def update_order_providers(self):
        if self.use_order_providers:
            order_providers: list[OrderProvider] = await OrderProviderDAO.filter(filters=[
                OrderProvider.network_id == self.node.network.id
            ])
            self.order_providers = [
                order_provider.address
                for order_provider in order_providers
            ]

    async def setup_dependencies(self):
        await self.update_stable_coins()
        await self.update_order_providers()

    update_dependencies = setup_dependencies

    def send_to_task(self, message: Message):
        celery_app.send_task(
            self.task_path,
            kwargs=dict(
                message=message.to_json(),
            )
        )

    async def get_search_data(self) -> dict:
        # TODO
        return {
            # address: order_id
            'direct_payments': {},
            # provider_address: order_id
            'provider_payments': {},
        }

    async def scrape_block(self, block_number: int):
        block = await self.node.get_block_detail(block_number=block_number)
        search_data = await self.get_search_data()
        await asyncio.gather(*[
            self.scrape_transaction(
                transaction=transaction,
                search_data=search_data,
            )
            for transaction in block.get('transactions', [])
        ])

    async def handler(self):
        await self.setup_dependencies()
        start_block = await self.node.get_latest_block_number()

        while True:
            end_block = await self.storage.get() or await self.node.get_latest_block_number()
            if end_block - start_block >= self.block_pack_size:
                await asyncio.gather(*[
                    self.scrape_block(block_number=block_number)
                    for block_number in range(start_block, end_block + 1)
                ])
            else:
                await asyncio.sleep(self.sleep_after_new_block)

    async def start_with_params(self, start_block: Optional[int] = None, end_block: Optional[int] = None):
        if not start_block and not end_block:
            raise ValueError('')

        start_block = start_block or await self.node.get_latest_block_number()
        end_block = end_block or await self.node.get_latest_block_number()

        for block in range(start_block, end_block + 1):
            await self.scrape_block(block_number=block)

    @abc.abstractmethod
    async def scrape_transaction(self, transaction: dict, search_data: dict): ...
