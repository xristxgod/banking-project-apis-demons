from rest_framework import serializers

from apps.cryptocurrencies.models import Provider


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = (
            'address', 'abi',
        )
