from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from apps.cryptocurrencies.rest import serializers
from apps.cryptocurrencies.models import Provider


class ProviderAPIView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()

    @classmethod
    def get_provider_object(cls, pk: int):
        return get_object_or_404(Provider, pk=pk)

    @extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: serializers.ProviderSerializer(),
        },
        summary='Provider',
        description='Provider',
    )
    def get(self, request, network_id: int, *args, **kwargs):
        return Response(
            serializers.ProviderSerializer(
                self.get_provider_object(network_id)
            ).data
        )
