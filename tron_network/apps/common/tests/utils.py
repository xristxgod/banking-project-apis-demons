import random

from faker.providers import BaseProvider
from faker.providers.currency.en_US import Provider
from tronpy.keys import PrivateKey


class TronProvider(Provider, BaseProvider):
    def _random_private_key_obj(self):
        return PrivateKey.random()

    def tron_private_key(self) -> str:
        return self._random_private_key_obj().hex()

    def tron_address(self) -> str:
        return self._random_private_key_obj().public_key.to_base58check_address()

    def tron_contract(self) -> tuple:
        symbol, name = self.cryptocurrency()
        return (
            self.tron_address(),
            symbol,
            name,
            random.randint(6, 10)
        )
