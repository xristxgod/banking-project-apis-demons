from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from apps.orders.models import Deposit
from apps.orders.rest import serializers


class DepositView(APIView):

    @classmethod
    def get_object(cls, pk: int):
        return get_object_or_404(Deposit, pk=pk)

    @extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: serializers.DepositSerializer(),
        },
        summary='Show Deposit',
        description='Show Deposit',
    )
    def get(self, request, pk: int, *args, **kwargs):
        return Response(
            serializers.DepositSerializer(
                self.get_object(pk)
            ).data
        )
