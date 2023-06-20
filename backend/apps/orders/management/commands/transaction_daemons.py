import abc
import asyncio
import decimal
import logging
from typing import Optional
from dataclasses import dataclass

import aioredis
import aio_pika
from django.db import transaction
from django.core.management.base import BaseCommand

import settings
from apps.cryptocurrencies.models import Currency, Wallet


@dataclass()
class MessageBody:
    id: str
    timestamp: int
    sender_address: str
    to_address: str
    network_id: int
    amount: decimal.Decimal
    commission: decimal.Decimal
    contract_address: Optional[str] = None
    order_id: Optional[int] = None


class AbstractDaemon(metaclass=abc.ABCMeta):
    network_id: int
    order_provider_address: str

    smart_contract_types: dict[str: str] = {}

    central_address: str

    class RedisBlockStorage:
        def __init__(self, key: int):
            self.key = key
            self.client = aioredis.from_url(settings.REDIS_URL, db=1)

        async def get(self) -> Optional[int]:
            return await self.client.get(self.key)

        async def set(self, value: int):
            await self.client.set(self.key, value)
            return value

    @classmethod
    def decoded_smart_contract_data(cls, data: str) -> tuple: ...

    @classmethod
    async def send_to_queue(cls, message: MessageBody) -> bool:
        # TODO
        async with aio_pika.connect_robust(settings.RABBITMQ_URL) as connect:
            pass

    @classmethod
    def get_addresses(cls):
        return Wallet.objects.filter(network_id=cls.network_id).values_list('address', flat=True)

    def __init__(self, **kwargs):
        self.logger = kwargs['logger']
        self.storage = self.RedisBlockStorage(self.network_id)
        self.contracts: dict[str: decimal.Decimal] = {}

        self.setup()

    def setup(self):
        self.contracts.update({
            contract.address: contract.decimal_place
            for contract in Currency.only_stable_coins_qs().filter(network_id=self.network_id)
        })

    update = setup

    @abc.abstractmethod
    async def latest_block_number(self) -> int: ...

    @abc.abstractmethod
    async def get_block(self, block_number) -> tuple: ...

    @abc.abstractmethod
    async def parsing_transaction(self, tx: dict, addresses: list[str], **kwargs) -> Optional[MessageBody]: ...

    async def parsing_block(self, block_number: int, addresses: list[str]) -> bool:
        transactions, extra = await self.get_block(block_number)
        if not transactions:
            return True

        raw_messages = await asyncio.gather(*[
            self.parsing_transaction(dict(tx), addresses=addresses, **extra)
            for tx in transactions
        ])

        success = await asyncio.gather(*[
            self.send_to_queue(message=message)
            for message in list(filter(lambda x: x is not None, raw_messages))
        ])

        return all(success)

    async def search(self):
        start = await self.storage.get() or await self.latest_block_number()
        while True:
            end = await self.latest_block_number()
            if start - end == 0:
                await asyncio.sleep(2)
                continue

            if start % 10 == 0:
                self.update()

            addresses = self.get_addresses()

            success = await asyncio.gather(*[
                self.parsing_block(block_number=block_number, addresses=addresses)
                for block_number in range(start, end+1)
            ])

            if all(success):
                self.logger.info(f'Daemon: {self.network_id} :: Success :: {start} to {end}')
                start = await self.storage.set(end + 1)
            else:
                self.logger.error(f'Daemon: {self.network_id} :: Error :: {start} to {end}')
                continue

    async def search_with_params(self, start_block: Optional[int] = None, end_block: Optional[int] = None,
                                 addresses: Optional[list[str]] = None):
        start_block = start_block or await self.latest_block_number()
        end_block = end_block or await self.latest_block_number()

        self.logger.info(f'Search Daemon: {self.network_id} :: {start_block} to {end_block}')
        addresses = addresses or self.get_addresses()
        success = await asyncio.gather(*[
            self.parsing_block(block_number=block_number, addresses=addresses)
            for block_number in range(start_block, end_block + 1)
        ])
        self.logger.info(f'Search Daemon: {self.network_id} :: {start_block} to {end_block} :: Result: {all(success)}')


class ETHDaemon(AbstractDaemon):
    network_id = 1
    order_provider_address = 'TODO'
    central_address = settings.ETH_CENTRAL_ADDRESS
    smart_contract_types = {
        '0x0753c30c': '(address,uint256)',
        '0xa9059cbb': '(address,uint256)',
        # TODO order provider type
    }

    def __init__(self, node_url: str, **kwargs):
        from web3 import AsyncWeb3, AsyncHTTPProvider
        from web3.middleware import geth_poa_middleware

        super().__init__(**kwargs)
        self.provider = AsyncHTTPProvider(endpoint_uri=node_url)
        self.client = AsyncWeb3(
            provider=self.provider,
            middlewares=[geth_poa_middleware, 0],
        )

    @classmethod
    def decoded_smart_contract_data(cls, data: str):
        import eth_abi

        fun_args_type = cls.smart_contract_types[data[:10]]
        return eth_abi.decode(fun_args_type, data[10:])

    async def latest_block_number(self) -> int:
        return await self.client.eth.block_number

    async def get_block(self, block_number) -> tuple:
        block = await self.client.eth.get_block(block_number, full_transactions=True)
        if not block['transactions']:
            return None, {}

        return block['transactions'], {'timestamp': block['timestamp']}

    async def parsing_transaction(self, tx: dict, addresses: list[str], **kwargs) -> Optional[MessageBody]:
        decoded_data = []
        order_id = None
        to_address = tx['to']
        contract_address = tx['to']

        if tx['data'] == '0x':
            address = tx['to']
            contract_address = None
        elif (
            tx['to'] in self.contracts.keys() and
            tx['data'][:10] in self.smart_contract_types.keys()
        ):
            # Stable coin transaction
            decoded_data = self.decoded_smart_contract_data(tx['data'])
            address = to_address = decoded_data[0]
        elif (
            tx['to'] == self.order_provider_address and
            tx['data'][:10] in self.smart_contract_types.keys()
        ):
            decoded_data = self.decoded_smart_contract_data(tx['data'])
            address = tx['from']
            order_id = decoded_data[0]
            to_address = self.central_address
        else:
            address = None

        if not address or address not in addresses:
            return None

        if contract_address and not order_id:
            # TODO amount and commission
            pass

        return MessageBody(
            id=tx['hash'].hex(),
            timestamp=kwargs['timestamp'],
            sender_address=tx['from'],
            to_address=to_address,
            network_id=self.network_id,
            amount='',
            commission='',
            contract_address=contract_address,
            order_id=order_id,
        )


class BSCDaemon(ETHDaemon):
    network_id = 2
    order_provider_address = 'TODO'
    central_address = settings.BSC_CENTRAL_ADDRESS
    smart_contract_types = {
        '0x0753c30c': '(address,uint256)',
        '0xa9059cbb': '(address,uint256)',
        # TODO order provider type
    }


class TRONDaemon(AbstractDaemon):
    network_id = 3
    order_provider_address = 'TODO'
    central_address = settings.TRON_CENTRAL_ADDRESS
    smart_contract_types = {
        '0x0753c30c': '(address,uint256)',
        '0xa9059cbb': '(address,uint256)',
        # TODO order provider type
    }

    def __init__(self, node_url: str, **kwargs):
        from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

        super().__init__(**kwargs)
        self.provider = AsyncHTTPProvider(endpoint_uri=node_url)
        self.client = AsyncTron(
            provider=self.provider,
        )

    @classmethod
    def decoded_smart_contract_data(cls, data: str):
        from tronpy.abi import tron_abi

        fun_args_type = cls.smart_contract_types[data[:10]]
        return tron_abi.decode_single(fun_args_type, data[10:])

    async def latest_block_number(self) -> int:
        return await self.client.get_latest_block_number()

    async def get_block(self, block_number) -> tuple:
        block = await self.client.get_block(block_number, visible=True)
        if not block['transactions']:
            return None, {}

        return block['transactions'], {}

    async def parsing_transaction(self, tx: dict, addresses: list[str], **kwargs) -> Optional[MessageBody]:
        decoded_data = []
        order_id = None
        to_address = tx['to']
        contract_address = tx['to']
        # TODO
        pass


class Command(BaseCommand):

    transaction_daemons_cls: dict[str: AbstractDaemon] = {
        'eth': ETHDaemon,
        'bsc': BSCDaemon,
        'tron': TRONDaemon,
    }

    @classmethod
    def _get_logger(cls) -> logging.Logger:
        return logging.getLogger(__file__)

    def _get_services(self, name: str) -> AbstractDaemon:
        return self.transaction_daemons_cls[name.lower()]

    def _get_params(self) -> dict: ...

    def handle(self, *args, **options):
        service = self._get_services(...)
        params = self._get_params()

        if params:
            coroutine = service.search_with_params(**params)
        else:
            coroutine = service.search()

        return asyncio.run(coroutine)
