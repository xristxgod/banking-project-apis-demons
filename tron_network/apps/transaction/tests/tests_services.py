import time
import uuid
import decimal

from tronpy.tron import PrivateKey

import pytest

from .factories import FakeTransactionBuilder, FakeTransaction, fake_amount
from core.crypto.tests.factories import fake_address, fake_private_key

from apps.transaction import services
from apps.transaction import schemas


class BaseTestTransaction:
    type: schemas.TransactionType

    cls_obj: services.BaseTransaction

    cls_body_create: schemas.BaseCreateTransactionSchema
    cls_response_create: schemas.ResponseCreateTransaction = schemas.ResponseCreateTransaction

    cls_body_send: schemas.BodySendTransaction = schemas.BodySendTransaction
    cls_response_sent: schemas.BaseResponseSendTransactionSchema


@pytest.mark.asyncio
class TestNativeTransfer(BaseTestTransaction):
    type = schemas.TransactionType.TRANSFER_NATIVE

    cls_obj = services.NativeTransfer

    cls_body_create = schemas.BodyCreateTransfer

    cls_response_sent = schemas.ResponseSendTransfer

    async def test_create(self, mocker):
        fake_id = str(uuid.uuid4())
        builder = FakeTransactionBuilder(id=fake_id)
        fee_limit = 60_000_000
        commission = dict(
            fee=decimal.Decimal(0),
            bandwidth=265,
            energy=0,
        )
        body = self.cls_body_create(
            from_address=fake_address(),
            to_address=fake_address(),
            amount=fake_amount(),
            fee_limit=fee_limit,
        )

        mocker.patch(
            'tronpy.async_tron.AsyncTrx.transfer',
            return_value=builder
        )
        mocker.patch(
            'core.crypto.calculator.FeeCalculator.calculate',
            return_value=commission
        )

        obj = await self.cls_obj.create(body)

        builder.assert_fee_limit(fee_limit)
        builder.assert_use_builder()

        assert getattr(obj, 'from_address') == body.from_address
        assert getattr(obj, 'to_address') == body.to_address
        assert getattr(obj, 'currency') == body.currency
        assert obj.type == self.type

        assert isinstance(obj.expected_commission_schema, schemas.ResponseCommission)
        assert obj.expected_commission_schema == schemas.ResponseCommission(**commission)

        assert not getattr(obj, '_is_signed')
        assert not getattr(obj, '_is_send')

        assert getattr(obj, '_raw_transaction') is None
        assert getattr(obj, '_transaction_info') is None

        assert isinstance(obj.to_schema, self.cls_response_create)
        assert obj.to_schema == self.cls_response_create(
            id=fake_id,
            commission=schemas.ResponseCommission(**commission)
        )

    async def test_send(self, mocker):
        expected_commission = dict(
            fee=decimal.Decimal(0),
            bandwidth=265,
            energy=0,
        )

        fake_id = str(uuid.uuid4())

        fake_raw_transaction = {
            'raw_data': {
                'timestamp': int(time.time())
            }
        }
        fake_transaction_info = {
            'fee': decimal.Decimal(1.1),
            'receipt': {
                'net_usage': 265,
            }
        }

        transaction = FakeTransaction(
            id=fake_id,
            raw_transaction=fake_raw_transaction,
            transaction_info=fake_transaction_info,
        )

        from_address = fake_address()
        to_address = fake_address()
        amount = fake_amount()

        fake_private_key_obj = PrivateKey(bytes.fromhex(fake_private_key()))

        assert not transaction._signed
        assert transaction._private_key is None

        obj = self.cls_obj(
            obj=transaction,
            expected_commission=expected_commission,
            type=self.type,
            amount=amount,
            from_address=from_address,
            to_address=to_address,
            currency='TRX',
        )

        try:
            await obj.send()
            raise AssertionError()
        except self.cls_obj.TransactionNotSign:
            pass

        await obj.sign(fake_private_key_obj)

        transaction.assert_sign(fake_private_key_obj)
        assert obj._is_signed

        transaction.is_expired = False

        assert not obj.is_expired

        response = await obj.send()

        assert isinstance(response, self.cls_response_sent)
        assert response == self.cls_response_sent(
            id=fake_id,
            timestamp=fake_raw_transaction['raw_data']['timestamp'],
            commission=schemas.ResponseCommission(
                fee=fake_transaction_info['fee'],
                bandwidth=265,
                energy=0,
            ),
            amount=amount,
            from_address=from_address,
            to_address=to_address,
            currency='TRX',
            type=self.type,
        )
