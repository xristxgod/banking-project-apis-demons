import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import ProviderFactory


@pytest.fixture
def api_client():
    return APIClient


@pytest.mark.django_db
class TestProviderAPIView:
    @classmethod
    def get_endpoint(cls, pk: int):
        return reverse('cryptocurrencies:provider', args=(pk,))

    def test_not_found(self, api_client):
        response = api_client().get(self.get_endpoint(1))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_success_by_provider(self, api_client):
        provider = ProviderFactory()

        response = api_client().get(self.get_endpoint(provider.pk))
        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            'address': provider.address,
            'abi': provider.abi
        }

    def test_success_by_network(self, api_client):
        provider = ProviderFactory()

        response = api_client().get(self.get_endpoint(provider.network.pk))
        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            'address': provider.address,
            'abi': provider.abi
        }
