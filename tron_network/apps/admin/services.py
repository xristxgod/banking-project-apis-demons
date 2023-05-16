import decimal

from tronpy.keys import PrivateKey

import settings
from core.crypto import node
from apps.transaction.endpoints import transaction


class Admin:

    def __init__(self, transaction_obj: transaction):
        self.address = settings.CENTRAL_WALLET_CONFIG['address']

        self._private_key = settings.CENTRAL_WALLET_CONFIG['private_key']
        self._mnemonic = settings.CENTRAL_WALLET_CONFIG['mnemonic']

        self._private_key_obj = PrivateKey(bytes.fromhex(self._private_key))

        self._transaction = transaction_obj
        self._node = node

    @property
    def transaction(self) -> transaction:
        return self._transaction

    async def balance(self, currency: str = 'TRX') -> decimal.Decimal:
        pass

    async def energy_balance(self) -> int:
        pass

    async def bandwidth_balance(self) -> bool:
        pass

    async def has_energy_balance(self) -> bool:
        pass

    async def has_bandwidth_balance(self) -> bool:
        pass

    async def has_native_balance(self) -> bool:
        pass
