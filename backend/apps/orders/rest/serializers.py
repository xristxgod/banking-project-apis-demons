from rest_framework import serializers

from apps.orders.models import OrderStatus, Deposit


class DepositDetailSerializer(serializers.Serializer):
    create = update = None
    currencyId = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=25, decimal_places=18)

    usdAmount = serializers.DecimalField(max_digits=25, decimal_places=2)
    usdCommission = serializers.DecimalField(max_digits=25, decimal_places=2)
    usdExchangeRate = serializers.DecimalField(max_digits=25, decimal_places=2)


class TransactionDetailSerializer(serializers.Serializer):
    create = update = None
    transactionHash = serializers.CharField()
    timestamp = serializers.IntegerField()
    senderAddress = serializers.CharField()
    recipientAddress = serializers.CharField()
    fee = serializers.DecimalField(max_digits=25, decimal_places=18)


class DepositSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    userId = serializers.IntegerField()

    status = serializers.IntegerField()
    verbose_status = serializers.CharField()

    detail = DepositDetailSerializer()

    transactionDetail = TransactionDetailSerializer(required=False, default=None)
    can_send = serializers.BooleanField()

    create = serializers.DateTimeField()
    update = serializers.DateTimeField()
    confirmed = serializers.DecimalField(default=None, required=False)

    @classmethod
    def _get_detail(cls, instance: Deposit):
        return DepositDetailSerializer(dict(
            currencyId=instance.order.currency_id,
            amount=instance.order.amount,
            usdAmount=instance.amount,
            usdCommission=instance.commission,
            usdExchangeRate=instance.usd_exchange_rate
        ))

    @classmethod
    def _get_transaction_detail(cls, instance: Deposit):
        if instance.order.status != OrderStatus.DONE:
            return

        transaction = getattr(instance.order, 'transaction', None)

        if not transaction:
            return

        return TransactionDetailSerializer(dict(
            transactionHash=transaction.transaction_hash,
            timestamp=transaction.timestamp,
            senderAddress=transaction.sender_address,
            recipientAddress=transaction.recipient_address,
            fee=transaction.fee,
        )).data

    def to_representation(self, instance: Deposit):
        return dict(
            id=instance.pk,
            userId=instance.costumer.pk,
            status=instance.status,
            verbose_status=instance.get_status_display(),
            detail=self._get_detail(instance),
            transactionDetail=self._get_transaction_detail(instance),
            can_send=instance.order.can_send,
            create=instance.create,
            update=instance.update,
            confirmed=instance.confirmed,
        )
