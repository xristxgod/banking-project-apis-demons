import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import DepositFactory


@pytest.fixture
def api_client():
    return APIClient


@pytest.mark.django_db
class TestDepositAPIView:
    @classmethod
    def get_endpoint(cls, pk: int):
        return reverse('orders:deposit', args=(pk,))

    def test_not_found(self, api_client):
        response = api_client().get(self.get_endpoint(1))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('params', [
        {'is_created': True},
        {'is_cancel': True},
        {'is_done': True},
    ])
    def test_success_response(self, params, api_client):
        deposit = DepositFactory(**params)

        response = api_client().get(self.get_endpoint(deposit.pk))
        assert response.status_code == status.HTTP_200_OK

        assert isinstance(response.json(), dict)
