import pytest

from apps.cryptocurrencies.rest import serializers

from .factories import NetworkFactory, CurrencyFactory, ProviderFactory


@pytest.mark.django_db
class TestNetworkSerializer:
    def test_serializer(self):
        obj = NetworkFactory()

        data = serializers.NetworkSerializer(obj).data

        assert data == {
            'pk': obj.pk,
            'name': obj.name,
            'url': obj.url,
            'block_explorer_url': obj.block_explorer_url,
            'chain_id': obj.chain_id,
        }


@pytest.mark.django_db
class TestCurrencySerializer:

    def test_serializer(self):
        from apps.cryptocurrencies.abi import ERC20
        obj = CurrencyFactory()

        data = serializers.CurrencySerializer(obj).data
        network_data = serializers.NetworkSerializer(obj.network).data

        assert data == {
            'pk': obj.pk,
            'name': obj.name,
            'symbol': obj.symbol,
            'decimal_place': obj.decimal_place,
            'address': obj.address,
            'network': network_data,
            'abi': obj.abi,
        }

        assert data['abi'] == ERC20
        assert data['network'] == network_data


@pytest.mark.django_db
class TestProviderSerializer:
    def test_serializer(self):
        from apps.cryptocurrencies.abi import PROVIDER

        obj = ProviderFactory()

        data = serializers.ProviderSerializer(obj).data

        assert data == {
            'pk': obj.pk,
            'address': obj.address,
            'abi': obj.abi,
        }

        assert data['abi'] == PROVIDER
