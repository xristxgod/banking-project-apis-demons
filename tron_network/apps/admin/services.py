import decimal
from typing import Type

from tronpy.keys import PrivateKey

import settings
from core.crypto import node
from apps.transaction.endpoints import transaction


class Admin:

    def __init__(self, transaction_obj: Type[transaction]):
        self.address = settings.CENTRAL_WALLET_CONFIG['address']

        self._private_key = settings.CENTRAL_WALLET_CONFIG['private_key']
        self._mnemonic = settings.CENTRAL_WALLET_CONFIG['mnemonic']

        self._private_key_obj = PrivateKey(bytes.fromhex(self._private_key))

        self._transaction = transaction_obj
        self._node = node

    @property
    def transaction(self) -> Type[transaction]:
        return self._transaction

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
