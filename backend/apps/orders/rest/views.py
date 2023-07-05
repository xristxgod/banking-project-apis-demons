from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from apps.orders import models
from apps.orders.rest import serializers


class PaymentAPIView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: serializers.PaymentSerializer(),
        },
        summary='Payment',
        description='Payment',
    )
    def get(self, request, pk: int, *args, **kwargs):
        obj = get_object_or_404(models.Payment, pk=pk)
        return Response(
            serializers.PaymentSerializer(obj).data
        )

    @extend_schema(
        request=serializers.UpdatePaymentSerializer(),
        responses={
            status.HTTP_200_OK: serializers.PaymentSerializer(),
        },
        summary='Update payment',
        description='Update payment',
    )
    def put(self, request, pk: int, *args, **kwargs):
        obj = get_object_or_404(models.Payment, pk=pk)
        serializer = serializers.UpdatePaymentSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializers.PaymentSerializer(obj).data
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)
