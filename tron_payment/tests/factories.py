import faker
from tronpy.tron import keys

from tests.utils import TronProvider


fake = faker.Faker()
fake.add_provider(TronProvider)


def fake_address(is_hex: bool = False) -> str:
    address = fake.unique.tron_address()
    if is_hex:
        address = keys.to_hex_address(address)
    return address


def fake_private_key() -> str:
    return fake.unique.tron_private_key()


def fake_stable_coin():
    """
    :return: TronProvider._FakeStableCoin
    """
    return fake.unique.tron_stable_coin()
