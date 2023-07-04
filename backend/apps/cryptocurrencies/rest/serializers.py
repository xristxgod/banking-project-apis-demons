from rest_framework import serializers

from apps.cryptocurrencies import models


class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Network
        fields = (
            'pk', 'name', 'url', 'block_explorer_url',
            'chain_id',
        )


class CurrencySerializer(serializers.ModelSerializer):
    network = NetworkSerializer(source='network')

    class Meta:
        model = models.Currency
        fields = (
            'pk', 'name', 'symbol',
            'decimal_place', 'address',
            'network',
        )


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Provider
        fields = (
            'pk', 'address', 'abi',
        )
