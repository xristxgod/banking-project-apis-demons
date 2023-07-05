from typing import Optional

from django.db import transaction
from rest_framework import serializers

from apps.orders import models
from apps.orders.services import update_payment_status


class OrderSerializer(serializers.ModelSerializer):
    verbose_status = serializers.CharField(source='get_status_display')

    class Meta:
        model = models.Order
        fields = (
            'pk', 'amount', 'currency_id',
            'user_id', 'status', 'verbose_status',
            'created', 'updated', 'confirmed',
        )


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = (
            'order_id', 'transaction_hash', 'timestamp',
            'sender_address', 'recipient_address', 'fee',
            'url',
        )


class TempWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TempWallet
        fields = (
            'address',
        )


class PaymentSerializer(serializers.ModelSerializer):
    can_send = serializers.BooleanField(source='order.can_send')
    verbose_type = serializers.CharField(source='get_type_display')
    order_detail = OrderSerializer(source='order')
    transaction_detail = serializers.SerializerMethodField()
    temp_wallet = serializers.SerializerMethodField()

    class Meta:
        model = models.Payment
        fields = (
            'pk', 'usdt_amount', 'usdt_exchange_rate', 'usdt_commission',
            'type', 'verbose_type', 'order_detail', 'transaction_detail',
            'can_send', 'temp_wallet',
        )

    @classmethod
    def get_transaction_detail(cls, instance: models.Payment) -> Optional[TransactionSerializer]:
        if (
                instance.status == models.OrderStatus.DONE and
                hasattr(instance.order, 'transaction')
        ):
            return TransactionSerializer(instance.order.transaction).data

    @classmethod
    def get_temp_wallet(cls, instance: models.Payment) -> Optional[TempWalletSerializer]:
        if instance.type == models.Payment.Type.DEPOSIT:
            return TempWalletSerializer(instance.temp_wallet).data


class UpdatePaymentSerializer(serializers.Serializer):
    create = update = None
    status = serializers.ChoiceField(choices=models.OrderStatus.choices)

    @transaction.atomic()
    def update(self, instance: models.Payment, validated_data):
        return update_payment_status(payment=instance, status=validated_data['status'])
