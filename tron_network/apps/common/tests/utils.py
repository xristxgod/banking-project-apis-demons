import random

from faker.providers import BaseProvider
from faker.providers.currency.en_US import Provider
from tronpy.keys import PrivateKey


class TronProvider(Provider, BaseProvider):
    def tron_address(self) -> str:
        priv_key = PrivateKey.random()
        return priv_key.public_key.to_base58check_address()

    def tron_contract(self) -> tuple:
        symbol, name = self.cryptocurrency()
        return (
            self.tron_address(),
            symbol,
            name,
            random.randint(6, 10)
        )
