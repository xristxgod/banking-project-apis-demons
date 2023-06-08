import decimal
import random
from typing import Optional

import faker
from tronpy.tron import keys

from core.utils import to_sun
from core.schemas import TransactionType
from tests.utils import TronProvider, FakeRawTransaction


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


def fake_amount(decimal_place: int = 6) -> decimal.Decimal:
    return fake.unique.pydecimal(
        left_digits=5,
        right_digits=decimal_place,
        positive=True,
    )


def random_resource() -> str:
    return ['ENERGY', 'BANDWIDTH'][random.randint(0, 1)]


def fake_transaction(typ: TransactionType, owner: Optional[str] = None, is_signed: bool = True, **params) -> dict:

    owner = owner or fake_address()
    amount = params.get('amount') or fake_amount(decimal_place=params.get('decimal_place', 6))

    match typ:
        case TransactionType.TRANSFER:
            params['to_address'] = params.get('to_address') or fake_address()

            if params.get('contract_address') and params.get('decimal_place'):
                params['amount'] = int(amount * 10 ** params['decimal_place'])
            else:
                params['amount'] = to_sun(amount)
        case TransactionType.FREEZE | TransactionType.UNFREEZE:
            params['resource'] = params.get('resource') or random_resource()
            params['amount'] = to_sun(amount)
        case TransactionType.APPROVE | TransactionType.TRANSFER_FROM:
            params['to_address'] = params.get('to_address') or fake_address()
            params['contract_address'] = params.get('contract_address') or fake_address()
            params['decimal_place'] = params.get('decimal_place') or random.randint(6, 18)
            params['amount'] = int(amount * 10 ** params['decimal_place'])

            if typ == TransactionType.TRANSFER_FROM:
                params['from_address'] = params.get('from_address') or fake_address()
        case _:
            raise ValueError()

    return FakeRawTransaction(owner=owner, typ=typ, is_signed=is_signed, **params).result
