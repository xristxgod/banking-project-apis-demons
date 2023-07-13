from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from apps.cryptocurrencies import models
from apps.cryptocurrencies.rest import serializers


@api_view(['GET'])
@extend_schema(
    request=None,
    responses={
        status.HTTP_200_OK: serializers.NetworkSerializer(),
    },
    summary='Network',
    description='Network',
)
def network_view(request, pk: int):
    obj = get_object_or_404(models.Network, pk=pk)
    return Response(serializers.NetworkSerializer(obj).data)


@api_view(['GET'])
@extend_schema(
    request=None,
    responses={
        status.HTTP_200_OK: serializers.CurrencySerializer(),
    },
    summary='Currency',
    description='Currency',
)
def currency_view(request, pk: int):
    obj = get_object_or_404(models.Currency, pk=pk)
    return Response(serializers.CurrencySerializer(obj).data)


@api_view(['GET'])
@extend_schema(
    request=None,
    responses={
        status.HTTP_200_OK: serializers.ProviderSerializer(),
    },
    summary='Provider',
    description='Provider',
)
def provider_view(request, pk: int):
    obj = get_object_or_404(models.Provider, pk=pk)
    return Response(serializers.ProviderSerializer(obj).data)
