from typing import Optional

from rest_framework import serializers

from apps.orders import models


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


class PaymentSerializer(serializers.ModelSerializer):
    can_send = serializers.BooleanField(source='order.can_send')
    verbose_type = serializers.CharField(source='get_type_display()')
    order_detail = OrderSerializer()
    transaction_detail = serializers.SerializerMethodField()

    class Meta:
        model = models.Payment
        fields = (
            'pk', 'usdt_amount', 'usdt_exchange_rate', 'usdt_commission',
            'type', 'verbose_type', 'order_detail', 'transaction_detail',
            'can_send',
        )

    @classmethod
    def _get_transaction_detail(cls, instance: models.Payment) -> Optional[TransactionSerializer]:
        if (
                instance.status != models.OrderStatus.DONE or
                not hasattr(instance.order, 'transaction')
        ):
            return

        return TransactionSerializer(instance.order.transaction).data
