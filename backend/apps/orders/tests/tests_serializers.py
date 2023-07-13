import pytest

from apps.orders.rest import serializers
from apps.orders.models import Payment

from .utils import decimal_to_str, correct_datetime
from .factories import OrderFactory, TransactionFactory, PaymentFactory, TempWalletFactory


@pytest.mark.django_db
class TestOrderSerializer:
    factory = OrderFactory
    serializer = serializers.OrderSerializer

    def test_serializer(self):
        obj = self.factory()

        assert self.serializer(obj).data == {
            'pk': obj.pk,
            'amount': decimal_to_str(obj.amount),
            'currency_id': obj.currency_id,
            'user_id': obj.user_id,
            'status': obj.status,
            'verbose_status': obj.get_status_display(),
            'created': correct_datetime(obj.created),
            'updated': correct_datetime(obj.updated),
            'confirmed': correct_datetime(obj.confirmed),
        }


@pytest.mark.django_db
class TestTransactionSerializer:
    factory = TransactionFactory
    serializer = serializers.TransactionSerializer

    def test_serializer(self):
        obj = self.factory()

        assert self.serializer(obj).data == {
            'order_id': obj.order_id,
            'transaction_hash': obj.transaction_hash,
            'timestamp': obj.timestamp,
            'sender_address': obj.sender_address,
            'recipient_address': obj.recipient_address,
            'fee': decimal_to_str(obj.fee),
            'url': obj.url,
        }


@pytest.mark.django_db
class TestPaymentSerializer:
    factory = PaymentFactory
    serializer = serializers.PaymentSerializer

    @pytest.mark.parametrize('params', [
        {'is_created': True},
        {'is_cancel': True},
    ])
    def test_deposit(self, params):
        deposit = self.factory(
            type=Payment.Type.DEPOSIT,
            **params,
        )
        temp_wallet = TempWalletFactory(deposit=deposit)

        data = self.serializer(deposit).data
        assert data == {
            'pk': deposit.pk,
            'usdt_amount': decimal_to_str(deposit.usdt_amount),
            'usdt_exchange_rate': decimal_to_str(deposit.usdt_exchange_rate),
            'usdt_commission': decimal_to_str(deposit.usdt_commission),
            'type': deposit.type,
            'verbose_type': deposit.get_type_display(),
            'order_detail': serializers.OrderSerializer(deposit.order).data,
            'transaction_detail': None,
            'can_send': deposit.order.can_send,
            'temp_wallet': {
                'address': temp_wallet.address,
            },
        }

        if params.get('is_created'):
            assert data['can_send']
        elif params.get('is_cancel'):
            assert not data['can_send']

    def test_deposit_done(self):
        deposit = self.factory(
            type=Payment.Type.DEPOSIT,
            is_done=True,
        )
        temp_wallet = TempWalletFactory(deposit=deposit)

        assert self.serializer(deposit).data == {
            'pk': deposit.pk,
            'usdt_amount': decimal_to_str(deposit.usdt_amount),
            'usdt_exchange_rate': decimal_to_str(deposit.usdt_exchange_rate),
            'usdt_commission': decimal_to_str(deposit.usdt_commission),
            'type': deposit.type,
            'verbose_type': deposit.get_type_display(),
            'order_detail': serializers.OrderSerializer(deposit.order).data,
            'transaction_detail': serializers.TransactionSerializer(deposit.order.transaction).data,
            'can_send': False,
            'temp_wallet': {
                'address': temp_wallet.address,
            },
        }

    @pytest.mark.parametrize('params', [
        {'is_created': True},
        {'is_cancel': True},
        {'is_done': True},
    ])
    def test_by_provider_deposit(self, params):
        deposit = self.factory(
            type=Payment.Type.BY_PROVIDER_DEPOSIT,
            **params,
        )

        data = self.serializer(deposit).data

        assert not data['temp_wallet']

    @pytest.mark.parametrize('params', [
        {'is_created': True},
        {'is_cancel': True},
        {'is_done': True},
    ])
    def test_withdraw(self, params):
        withdraw = self.factory(
            type=Payment.Type.WITHDRAW,
            **params,
        )

        data = self.serializer(withdraw).data

        assert not data['temp_wallet']
