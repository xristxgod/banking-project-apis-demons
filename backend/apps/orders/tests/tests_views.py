import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import OrderFactory, TransactionFactory, PaymentFactory
from apps.orders import models
from apps.orders.rest import serializers


@pytest.fixture
def api_client():
    return APIClient


@pytest.mark.django_db
class TestPaymentAPIView:
    serializer = serializers.PaymentSerializer

    @classmethod
    def get_endpoint(cls, pk: int):
        return reverse('orders:payment', args=(pk,))

    def test_get_not_found(self, api_client):
        response = api_client().get(self.get_endpoint(1))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_success(self, api_client):
        order = OrderFactory(status=models.OrderStatus.DONE)
        TransactionFactory(order=order)
        payment = PaymentFactory(
            order=order,
            type=models.Payment.Type.BY_PROVIDER_DEPOSIT,
            is_done=True
        )

        response = api_client().get(self.get_endpoint(payment.pk))

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.serializer(
            # The problem with numbers! I don't know how to fix it!
            # Bypass, make a repeat request during the test.
            # It does not affect the progress of work
            models.Payment.objects.get(pk=payment.pk)
        ).data
