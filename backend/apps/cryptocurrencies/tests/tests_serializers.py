import pytest

from apps.cryptocurrencies.rest import serializers

from .factories import ProviderFactory


@pytest.mark.django_db
class TestProviderSerializer:
    def test_provider(self):
        from apps.cryptocurrencies.abi import PROVIDER

        provider = ProviderFactory()

        data = serializers.ProviderSerializer(provider).data

        assert data == {
            'address': provider.address,
            'abi': provider.abi,
        }

        assert data['abi'] == PROVIDER
