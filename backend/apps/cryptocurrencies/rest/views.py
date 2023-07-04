from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from apps.cryptocurrencies.rest import serializers
from apps.cryptocurrencies.models import Provider


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
    obj = get_object_or_404(Provider, pk=pk)
    return Response(serializers.ProviderSerializer(obj).data)
