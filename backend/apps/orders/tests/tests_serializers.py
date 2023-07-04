import pytest

from apps.orders.rest import serializers

from .utils import decimal_to_str, correct_datetime
from .factories import OrderFactory, TransactionFactory, PaymentFactory


@pytest.mark.django_db
class TestOrderSerializer:
    serializer = serializers.OrderSerializer

    def test_serializer(self):
        obj = OrderFactory()

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
