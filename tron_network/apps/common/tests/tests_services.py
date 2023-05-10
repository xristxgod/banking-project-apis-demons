import decimal

import pytest

from apps.common import schemas
from apps.common import services

from .factories import fake_address, create_fake_contract


@pytest.mark.asyncio
async def test_create_wallet():
    from tronpy.keys import is_address
    from apps.common.utils import generate_mnemonic, generate_passphrase

    mnemonic = generate_mnemonic()
    passphrase = generate_passphrase()

    body = schemas.BodyCreateWallet(
        mnemonic=mnemonic,
        passphrase=passphrase,
    )

    response = await services.create_wallet(body)

    assert response.mnemonic == mnemonic
    assert response.passphrase == passphrase
    assert is_address(response.address)


@pytest.mark.asyncio
@pytest.mark.parametrize('currency, balance', [
    ('TRX', decimal.Decimal(12.4)),
    ('USDT', decimal.Decimal(22.45)),
])
async def test_wallet_balance(currency: str, balance: decimal.Decimal, mocker):
    address = fake_address()

    if currency != 'TRX':
        await create_fake_contract(symbol=currency)
        mocker.patch(
            'core.crypto.contract.Contract.balance_of',
            return_value=balance
        )
    else:
        mocker.patch(
            'tronpy.async_tron.AsyncTron.get_account_balance',
            return_value=balance
        )

    body = schemas.BodyWalletBalance(
        address=address,
        currency=currency,
    )

    response = await services.wallet_balance(body)

    assert response.balance == balance
