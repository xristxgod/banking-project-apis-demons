import decimal
import functools
from typing import Type, Callable

import aioredis
from tronpy.keys import PrivateKey

import settings
from core.crypto import node
from apps.admin import schemas
from apps.transaction.endpoints import transaction


class AdminWalletIndexController:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.client = aioredis.from_url(redis_url)

    def __str__(self):
        return 'admin_wallet_index'

    async def get(self) -> int:
        return await self.client.get(self)

    async def save(self, number: int):
        await self.client.sadd(self, number)


class Admin:

    def __init__(self, transaction_obj: Type[transaction]):
        self.address = settings.CENTRAL_WALLET_CONFIG['address']

        self._private_key = settings.CENTRAL_WALLET_CONFIG['private_key']
        self._mnemonic = settings.CENTRAL_WALLET_CONFIG['mnemonic']

        self._private_key_obj = PrivateKey(bytes.fromhex(self._private_key))

        self._transaction = transaction_obj
        self._index = AdminWalletIndexController()
        self._node = node

    @property
    def transaction(self) -> Type[transaction]:
        return self._transaction

    @staticmethod
    def wallet_index(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, body: schemas.BodyAdminCreateWallet):
            if body.index is None:
                body.index = await self._index.get()

            current_index = body.index
            result = await func(self, body)
            assert isinstance(result, schemas.ResponseAdminCreateWallet)
            await self._index.save(current_index + 1)
            return result
        return wrapper

    @wallet_index
    async def create_sub_wallet(self, body: schemas.BodyAdminCreateWallet) -> schemas.ResponseAdminCreateWallet:
        response = self._node.client.generate_address_from_mnemonic(
            self._mnemonic,
            account_path=body.index,
        )
        return schemas.ResponseAdminCreateWallet(
            private_key=response['private_key'],
            public_key=response['public_key'],
            address=response['base58check_address'],
        )

    async def balance(self, currency: str = 'TRX') -> decimal.Decimal:
        return await self._node.get_account_balance(self.address, currency=currency)

    async def energy_balance(self) -> int:
        return await self._node.get_energy_balance(self.address)

    async def bandwidth_balance(self) -> bool:
        return await self._node.get_bandwidth_balance(self.address)

    async def has_energy_balance(self) -> bool:
        return await self.energy_balance() > settings.CENTRAL_WALLET_CONFIG['min_balance']['energy']

    async def has_bandwidth_balance(self) -> bool:
        return await self.bandwidth_balance() > settings.CENTRAL_WALLET_CONFIG['min_balance']['bandwidth']

    async def has_native_balance(self) -> bool:
        return await self.balance('TRX') > settings.CENTRAL_WALLET_CONFIG['min_balance']['energy']
