import uuid
import decimal

import pytest

from .factories import FakeTransactionBuilder, fake_amount
from core.crypto.tests.factories import fake_address

from apps.transaction import services
from apps.transaction import schemas


@pytest.mark.asyncio
class TestNativeTransfer:
    type = schemas.TransactionType.TRANSFER_NATIVE

    cls_obj = services.NativeTransfer

    cls_body_create = schemas.BodyCreateTransfer
    cls_response_create = schemas.ResponseCreateTransaction

    cls_body_send = schemas.BodySendTransaction
    cls_response_send = schemas.ResponseSendTransfer

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
