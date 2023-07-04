import pytest

from apps.orders.rest import serializers

from .utils import decimal_to_str, correct_datetime
from .factories import OrderFactory, TransactionFactory, PaymentFactory


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

    def test_serializer(self):
        pass