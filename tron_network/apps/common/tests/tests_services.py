import pytest

from apps.common import schemas
from apps.common import services


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

    result = await services.create_wallet(body)

    assert result.mnemonic == mnemonic
    assert result.passphrase == passphrase
    assert is_address(result.address)


@pytest.mark.asyncio
@pytest.mark.parametrize('currency', [
    'TRX',
    'USDT',
])
async def test_wallet_balance(currency: str):
    pass
