import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.cryptocurrencies.rest import serializers
from .factories import NetworkFactory, CurrencyFactory, ProviderFactory


@pytest.fixture
def api_client():
    return APIClient


@pytest.mark.django_db
class TestNetworkView:
    serializer = serializers.NetworkSerializer

    @classmethod
    def get_endpoint(cls, pk: int):
        return reverse('cryptocurrencies:network', args=(pk,))

    def test_not_found(self, api_client):
        response = api_client().get(self.get_endpoint(1))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_success(self, api_client):
        obj = NetworkFactory()
        response = api_client().get(self.get_endpoint(obj.pk))

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == self.serializer(obj).data


@pytest.mark.django_db
class TestCurrencyView:
    serializer = serializers.CurrencySerializer

    @classmethod
    def get_endpoint(cls, pk: int):
        return reverse('cryptocurrencies:currency', args=(pk,))

    def test_not_found(self, api_client):
        response = api_client().get(self.get_endpoint(1))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_success(self, api_client):
        obj = CurrencyFactory()
        response = api_client().get(self.get_endpoint(obj.pk))

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == self.serializer(obj).data


@pytest.mark.django_db
class TestProviderView:
    serializer = serializers.ProviderSerializer

    @classmethod
    def get_endpoint(cls, pk: int):
        return reverse('cryptocurrencies:provider', args=(pk,))

    def test_not_found(self, api_client):
        response = api_client().get(self.get_endpoint(1))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_success(self, api_client):
        obj = ProviderFactory()
        response = api_client().get(self.get_endpoint(obj.pk))

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == self.serializer(obj).data
