import decimal
import time
import uuid
from typing import Type, Optional

import pytest

from apps.common import schemas
from apps.common import services
from apps.common.services import TransactionType
from core.crypto.calculator import FEE_METHOD_TYPES
from core.crypto.utils import from_sun, to_sun
from .factories import fake_private_key, fake_address, create_fake_contract


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


@pytest.mark.parametrize(
    'method, parameter, bandwidth_balance, energy_balance, is_to_address_active, energy_used',
    [(
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
    ), (
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
    ), (
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
    ), (
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
    ), (
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
    ), (
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
    ), (
            FEE_METHOD_TYPES.APPROVE,
            {
                'owner_address': fake_address(),
                'spender_address': fake_address(),
                'amount': decimal.Decimal(15.1),
                'currency': 'USDT',
            },
            0,
            0,
            True,
            12_000,
    ),
        # TODO: Add when new ones appear
    ]
)
async def test_fee_calculator(method: FEE_METHOD_TYPES, parameter: dict, bandwidth_balance: int,
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


@pytest.mark.asyncio
class TestTransfer:
    create_transfer_obj = services.CreateTransfer

    @pytest.mark.parametrize(
        'body, fee, native_balance, token_balance, exception',
        [(
                schemas.BodyCreateTransfer(
                    from_address=fake_address(),
                    to_address=fake_address(),
                    amount=decimal.Decimal(12.4),
                    currency='TRX',
                ),
                0,
                decimal.Decimal(100),
                None,
                None,
        ), (
                schemas.BodyCreateTransfer(
                    from_address=fake_address(),
                    to_address=fake_address(),
                    amount=decimal.Decimal(100),
                    currency='TRX',
                ),
                decimal.Decimal(0.267),
                decimal.Decimal(100),
                None,
                services.InvalidCreateTransaction,
        ), (
                schemas.BodyCreateTransfer(
                    from_address=fake_address(),
                    to_address=fake_address(),
                    amount=decimal.Decimal(15),
                    currency='USDT',
                ),
                decimal.Decimal(13.99),
                decimal.Decimal(100),
                decimal.Decimal(170),
                None,
        ), (
                schemas.BodyCreateTransfer(
                    from_address=fake_address(),
                    to_address=fake_address(),
                    amount=decimal.Decimal(200),
                    currency='USDT',
                ),
                decimal.Decimal(13.99),
                decimal.Decimal(100),
                decimal.Decimal(170),
                services.InvalidCreateTransaction,
        ), (
                schemas.BodyCreateTransfer(
                    from_address=fake_address(),
                    to_address=fake_address(),
                    amount=decimal.Decimal(100),
                    currency='USDT',
                ),
                decimal.Decimal(13.99),
                decimal.Decimal(12),
                decimal.Decimal(170),
                services.InvalidCreateTransaction,
        )]
    )
    async def test_valid(self, body: schemas.BodyCreateTransfer, fee: decimal.Decimal,
                         native_balance: decimal.Decimal, token_balance: decimal.Decimal,
                         exception: Optional[Type[Exception]], mocker):
        mocker.patch(
            'tronpy.async_tron.AsyncTron.get_account_balance',
            return_value=native_balance,
        )
        mocker.patch(
            'core.crypto.contract.Contract.balance_of',
            return_value=token_balance,
        )

        if not exception:
            assert await self.create_transfer_obj.valid(
                body=body, fee=fee
            ) is None
        else:
            with pytest.raises(exception) as err:
                await self.create_transfer_obj.valid(
                    body=body, fee=fee
                )

    @pytest.mark.parametrize(
        'currency, commission',
        [(
                'TRX',
                {
                    'fee': 0,
                    'bandwidth': 267,
                    'energy': 0,
                }
        ), (
                'USDT',
                {
                    'fee': decimal.Decimal(13.2),
                    'bandwidth': 365,
                    'energy': 12_000,
                }
        )]
    )
    async def test_create(self, currency: str, commission: dict, mocker):
        mocker.patch(
            'core.crypto.calculator.FeeCalculator.calculate',
            return_value=commission,
        )
        mocker.patch(
            'apps.common.services.CreateTransfer.valid',
            side_effect=None,
        )
        # There is no point in testing, the standard functionality is used, which has
        # already been tested in the `tronpy` library itself
        mocker.patch(
            'apps.common.services.CreateTransfer._create',
            return_value={},
        )

        body = schemas.BodyCreateTransfer(
            from_address=fake_address(),
            to_address=fake_address(),
            amount=decimal.Decimal(12.4),
            currency=currency,
        )

        response = await self.create_transfer_obj.create(body)

        assert isinstance(response, schemas.ResponseCreateTransaction)
        assert response.payload_dict == {
            'data': {},
            'extra': {
                'amount': str(body.amount),
                'from_address': body.from_address,
                'to_address': body.to_address,
                'currency': body.currency,
                'type': TransactionType.TRANSFER.value,
            }
        }

        assert response.commission == commission


@pytest.mark.asyncio
class TestApprove:
    create_approve_obj = services.CreateApprove

    @pytest.mark.parametrize(
        'body, fee, native_balance, exception',
        [(
                schemas.BodyCreateApprove(
                    owner_address=fake_address(),
                    spender_address=fake_address(),
                    amount=decimal.Decimal(12.4),
                    currency='USDT',
                ),
                decimal.Decimal(12.43),
                decimal.Decimal(100),
                None,
        ), (
                schemas.BodyCreateApprove(
                    owner_address=fake_address(),
                    spender_address=fake_address(),
                    amount=decimal.Decimal(12.4),
                    currency='USDT',
                ),
                decimal.Decimal(12.43),
                decimal.Decimal(0),
                services.InvalidCreateTransaction,
        )]
    )
    async def test_valid(self, body: schemas.BodyCreateApprove, fee: decimal.Decimal,
                         native_balance: decimal.Decimal, exception: Optional[Type[Exception]],
                         mocker):
        mocker.patch(
            'tronpy.async_tron.AsyncTron.get_account_balance',
            return_value=native_balance,
        )

        if not exception:
            assert await self.create_approve_obj.valid(
                body=body, fee=fee
            ) is None
        else:
            with pytest.raises(exception) as err:
                await self.create_approve_obj.valid(
                    body=body, fee=fee
                )

    @pytest.mark.parametrize(
        'currency, commission',
        [(
                'USDT',
                {
                    'fee': decimal.Decimal(13.2),
                    'bandwidth': 365,
                    'energy': 12_000,
                }
        ), (
                'USDC',
                {
                    'fee': decimal.Decimal(13.2),
                    'bandwidth': 365,
                    'energy': 12_000,
                }
        )]
    )
    async def test_create(self, currency: str, commission: dict, mocker):
        mocker.patch(
            'core.crypto.calculator.FeeCalculator.calculate',
            return_value=commission,
        )
        mocker.patch(
            'apps.common.services.CreateApprove.valid',
            side_effect=None,
        )
        # There is no point in testing, the standard functionality is used, which has
        # already been tested in the `tronpy` library itself
        mocker.patch(
            'apps.common.services.CreateApprove._create',
            return_value={},
        )

        body = schemas.BodyCreateApprove(
            owner_address=fake_address(),
            spender_address=fake_address(),
            amount=decimal.Decimal(12.4),
            currency=currency,
        )

        response = await self.create_approve_obj.create(body)

        assert isinstance(response, schemas.ResponseCreateTransaction)
        assert response.payload_dict == {
            'data': {},
            'extra': {
                'amount': str(body.amount),
                'from_address': body.owner_address,
                'to_address': body.spender_address,
                'currency': body.currency,
                'type': TransactionType.APPROVE.value,
            }
        }

        assert response.commission == commission


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'payload, transaction_info',
    [(
            {
                'data': {},
                'extra': {
                    'amount': decimal.Decimal(12.4),
                    'from_address': fake_address(),
                    'to_address': fake_address(),
                    'currency': 'TRX',
                    'type': TransactionType.TRANSFER.value,
                }
            },
            {
                'id': uuid.uuid4().hex,
                'blockTimeStamp': int(time.time()),
            }
    ), (
            {
                'data': {},
                'extra': {
                    'amount': decimal.Decimal(122.4),
                    'from_address': fake_address(),
                    'to_address': fake_address(),
                    'currency': 'USDT',
                    'type': TransactionType.TRANSFER.value,
                }
            },
            {
                'id': uuid.uuid4().hex,
                'blockTimeStamp': int(time.time()),
                'fee': to_sun(decimal.Decimal(12.2)),
            }
    ), (
            {
                'data': {},
                'extra': {
                    'amount': decimal.Decimal(122.4),
                    'from_address': fake_address(),
                    'to_address': fake_address(),
                    'currency': 'USDT',
                    'type': TransactionType.APPROVE.value,
                }
            },
            {
                'id': uuid.uuid4().hex,
                'blockTimeStamp': int(time.time()),
                'fee': to_sun(decimal.Decimal(12.2)),
            }
    ), (
            {
                'data': {},
                'extra': {
                    'amount': decimal.Decimal(122.4),
                    'from_address': fake_address(),
                    'to_address': fake_address(),
                    'currency': 'USDT',
                    'owner_address': fake_address(),
                    'type': TransactionType.TRANSFER_FROM.value,
                }
            },
            {
                'id': uuid.uuid4().hex,
                'blockTimeStamp': int(time.time()),
                'fee': to_sun(decimal.Decimal(12.2)),
            }
    ),]
)
async def test_send_transaction(payload: dict, transaction_info: dict, mocker):
    import json
    from tronpy.keys import PrivateKey

    private_key = fake_private_key()

    body = schemas.BodySendTransaction(
        payload=json.dumps(payload, default=str),
        private_key=private_key,
    )

    assert isinstance(body.private_key_obj, PrivateKey)
    assert body.payload_dict == json.loads(json.dumps(payload, default=str))
    assert body.extra == json.loads(json.dumps(payload['extra'], default=str))

    mocker.patch(
        'apps.common.schemas.BodySendTransaction.create_transaction_obj',
        return_value=None,
    )
    # There is no point in testing, the standard functionality is used, which has
    # already been tested in the `tronpy` library itself
    mocker.patch(
        'apps.common.services.SendTransaction._send_transaction',
        return_value=transaction_info,
    )
    obj = services.SendTransaction

    response = await obj.send_transaction(body)

    assert isinstance(response, schemas.ResponseSendTransaction)

    fee = transaction_info.get('fee', 0)
    if fee > 0:
        fee = from_sun(fee)

    assert response == schemas.ResponseSendTransaction(
        transaction_id=transaction_info['id'],
        timestamp=transaction_info['blockTimeStamp'],
        fee=fee,
        amount=payload['extra']['amount'],
        from_address=payload['extra']['from_address'],
        to_address=payload['extra']['to_address'],
        currency=payload['extra']['currency'],
        extra=schemas.ResponseSendTransactionExtra(
            type=payload['extra']['type'],
            owner_address=payload['extra'].get('owner_address'),
        )
    )