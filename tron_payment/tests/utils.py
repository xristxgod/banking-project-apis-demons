import random
from collections import namedtuple

from faker.providers import BaseProvider
from faker.providers.currency.en_US import Provider
from tronpy.keys import PrivateKey


class TronProvider(Provider, BaseProvider):

    FakeStableCoin = namedtuple('FakeStableCoin', field_names=[
        'address', 'symbol', 'name', 'decimal_place',
    ])

    @staticmethod
    def _random_private_key_obj():
        return PrivateKey.random()

    def tron_private_key(self) -> str:
        return self._random_private_key_obj().hex()

    def tron_address(self) -> str:
        return self._random_private_key_obj().public_key.to_base58check_address()

    def tron_stable_coin(self):
        symbol, name = self.cryptocurrency()
        return self.FakeStableCoin(
            address=self.tron_address(),
            symbol=symbol,
            name=name,
            decimal_place=random.randint(6, 18),
        )
