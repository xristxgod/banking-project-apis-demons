from rest_framework import serializers

from apps.orders.models import OrderStatus, Deposit


class PaymentDetailSerializer(serializers.Serializer):
    create = update = None
    usdAmount = serializers.DecimalField(max_digits=25, decimal_places=2)
    usdCommission = serializers.DecimalField(max_digits=25, decimal_places=2)
    usdExchangeRate = serializers.DecimalField(max_digits=25, decimal_places=2)


class OrderDetailSerializer(serializers.Serializer):
    create = update = None
    amount = serializers.DecimalField(max_digits=25, decimal_places=25)
    networkId = serializers.IntegerField()
    networkName = serializers.CharField()
    currencyId = serializers.IntegerField()
    currencySymbol = serializers.CharField()


class TransactionDetailSerializer(serializers.Serializer):
    create = update = None
    transactionHash = serializers.CharField()
    timestamp = serializers.IntegerField()
    senderAddress = serializers.CharField()
    recipientAddress = serializers.CharField()
    fee = serializers.DecimalField(max_digits=25, decimal_places=25)


class DepositSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    userId = serializers.IntegerField()

    status = serializers.ChoiceField(choices=OrderStatus.choices)
    verbose_status = serializers.CharField()

    chainId = serializers.IntegerField(default=None)
    nodeUrl = serializers.URLField()

    paymentDetail = PaymentDetailSerializer()
    orderDetail = OrderDetailSerializer()
    transactionDetail = TransactionDetailSerializer(required=False, default=None)

    can_send = serializers.BooleanField()

    create = serializers.DateTimeField()
    update = serializers.DateTimeField()

    @classmethod
    def _get_payment_detail(cls, instance: Deposit):
        return PaymentDetailSerializer(dict(
            usdAmount=instance.amount,
            usdCommission=instance.commission,
            usdExchangeRate=instance.usd_exchange_rate,
        ))

    @classmethod
    def _get_order_detail(cls, instance: Deposit):
        order = instance.order
        return OrderDetailSerializer(dict(
            amount=order.amount,
            networkId=order.currency.network.pk,
            networkName=order.currency.network.name,
            currencyId=order.currency.pk,
            currencySymbol=order.currency.symbol,
        ))

    @classmethod
    def _get_transaction_detail(cls, instance: Deposit):
        if instance.order.status != OrderStatus.DONE:
            return
        transaction = instance.order.transaction
        return TransactionDetailSerializer(dict(
            transactionHash=transaction.transaction_hash,
            timestamp=transaction.timestamp,
            senderAddress=transaction.sender_address,
            recipientAddress=transaction.recipient_address,
            fee=transaction.fee,
        ))

    def to_representation(self, instance: Deposit):
        return dict(
            id=instance.pk,
            userId=instance.order.user_id,
            status=instance.order.status,
            verbose_status=instance.order.get_status_display(),
            chainId=instance.order.currency.network.chain_id,
            nodeUrl=instance.order.currency.network.url,
            paymentDetail=self._get_payment_detail(instance),
            orderDetail=self._get_order_detail(instance),
            transactionDetail=self._get_transaction_detail(instance),
            can_send=instance.order.can_send,
            create=instance.order.created,
            update=instance.order.updated,
        )
