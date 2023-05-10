import decimal
from typing import Optional

import pytest

from core.crypto.calculator import FEE_METHOD_TYPES
from core.crypto.utils import from_sun
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

    assert isinstance(response, schemas.ResponseCreateWallet)
    assert response.mnemonic == mnemonic
    assert response.passphrase == passphrase
    assert is_address(response.address)


@pytest.mark.asyncio
@pytest.mark.parametrize('currency, balance', [
    ('TRX', decimal.Decimal(12.4)),
    ('USDT', decimal.Decimal(22.45)),
])
async def test_wallet_balance(currency: str, balance: decimal.Decimal, mocker):
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
        address=fake_address(),
        currency=currency,
    )

    response = await services.wallet_balance(body)

    assert isinstance(response, schemas.ResponseWalletBalance)
    assert response.balance == balance


@pytest.mark.asyncio
@pytest.mark.parametrize('currency, amount', [
    ('USDT', decimal.Decimal(10000002.4)),
    ('USDC', decimal.Decimal(11240000002.45)),
])
async def test_allowance(currency: str, amount: decimal.Decimal, mocker):
    await create_fake_contract(symbol=currency)
    mocker.patch(
        'core.crypto.contract.Contract.allowance',
        return_value=amount
    )

    body = schemas.BodyAllowance(
        owner_address=fake_address(),
        spender_address=fake_address(),
        currency=currency,
    )

    response = await services.allowance(body)

    assert isinstance(response, schemas.ResponseAllowance)
    assert response.amount == amount


@pytest.mark.asyncio
class TestTransfer:

    @pytest.mark.parametrize(
        'method, parameter, bandwidth_balance, energy_balance, is_to_address_active, energy_used',
        [
            (
                    FEE_METHOD_TYPES.TRANSFER,
                    {
                        'from_address': fake_address(),
                        'to_address': fake_address(),
                        'amount': decimal.Decimal(15.1),
                        'currency': 'TRX',
                    },
                    0,
                    1500,
                    True,
                    0,
            ),
            (
                    FEE_METHOD_TYPES.TRANSFER,
                    {
                        'from_address': fake_address(),
                        'to_address': fake_address(),
                        'amount': decimal.Decimal(15.1),
                        'currency': 'TRX',
                    },
                    0,
                    1500,
                    False,
                    0,
            ),
            (
                    FEE_METHOD_TYPES.TRANSFER,
                    {
                        'from_address': fake_address(),
                        'to_address': fake_address(),
                        'amount': decimal.Decimal(15.1),
                        'currency': 'TRX',
                    },
                    0,
                    0,
                    False,
                    0,
            ),
            (
                    FEE_METHOD_TYPES.TRANSFER,
                    {
                        'from_address': fake_address(),
                        'to_address': fake_address(),
                        'amount': decimal.Decimal(15.1),
                        'currency': 'USDT',
                    },
                    100_000,
                    1500,
                    True,
                    12_000,
            ),
            (
                    FEE_METHOD_TYPES.TRANSFER,
                    {
                        'from_address': fake_address(),
                        'to_address': fake_address(),
                        'amount': decimal.Decimal(15.1),
                        'currency': 'USDT',
                    },
                    0,
                    1500,
                    True,
                    12_000,
            ),
            (
                    FEE_METHOD_TYPES.TRANSFER,
                    {
                        'from_address': fake_address(),
                        'to_address': fake_address(),
                        'amount': decimal.Decimal(15.1),
                        'currency': 'USDT',
                    },
                    0,
                    0,
                    True,
                    12_000,
            ),
            # TODO: Add when new ones appear
        ])
    async def test_fee_calculator(self, method: FEE_METHOD_TYPES, parameter: dict, bandwidth_balance: int,
                                  energy_balance: int, is_to_address_active: bool, energy_used: Optional[int],
                                  mocker):
        from core.crypto.calculator import FeeCalculator

        mocker.patch(
            'core.crypto.node.Node.is_active_address',
            return_value=is_to_address_active
        )
        mocker.patch(
            'core.crypto.node.Node.get_bandwidth_balance',
            return_value=bandwidth_balance,
        )
        mocker.patch(
            'core.crypto.node.Node.get_energy_balance',
            return_value=energy_balance,
        )

        fee, bandwidth, energy = 0, 0, energy_used
        if parameter['currency'] == 'TRX':
            bandwidth += FeeCalculator.default_native_bandwidth_cost
            if not is_to_address_active:
                fee += FeeCalculator.activate_account_trx_cost
                bandwidth += FeeCalculator.activate_account_bandwidth_cost
            if bandwidth_balance < bandwidth:
                fee += FeeCalculator.not_bandwidth_balance_extra_fee_native_cost
        else:
            bandwidth += FeeCalculator.default_token_bandwidth_cost
            fee += from_sun(energy_used * FeeCalculator.energy_sun_cost)
            await create_fake_contract(symbol=parameter['currency'])
            mocker.patch(
                'core.crypto.contract.Contract.energy_used',
                return_value=energy_used
            )
            if bandwidth_balance < bandwidth:
                fee += FeeCalculator.not_bandwidth_balance_extra_fee_token_cost

        body = schemas.BodyCommission(parameter=parameter)

        response = await services.fee_calculator(body, method=method)

        assert isinstance(response, schemas.ResponseCommission)
        assert response.fee == fee
        assert response.bandwidth == bandwidth
        assert response.energy == energy
