from django.db import transaction
from django.core.management.base import BaseCommand

from apps.telegram.models import User
from apps.orders.models import Order, Transaction
from apps.cryptocurrencies.models import Network, InternalWallet


class Command(BaseCommand):
    """
    Message format:
        {
            'id': ...str: transaction hash...,
            'timestamp': ...int: timestamp...,
            'sender_address': ...str: sender address...,
            'to_address': ...str: to address...,
            'network_id': ...int: network id...,
            'contract_address': ...optional str: contract address...,   if not then native,
            'amount': ...decimal: amount...,
            'commission': ...decimal: commission...,
            'order_id': ...optional int: order id...,   if not then create new order
        }
    """

    def telegram_notification(self, user: User, order: Order):
        # TODO Изменить сообщения юзера на новое, что транзакция обрабатывается
        pass

    def take_message(self) -> list[dict]:
        # TODO добавить сбор сообщений из очереди
        pass

    @transaction.atomic()
    def create_transaction(self, message: dict, order: Order):
        obj = Transaction(
            order=order,
            transaction_hash=message['id'],
            timestamp=message['timestamp'],
            sender_address=message['sender_address'],
            to_address=message['to_address'],
            commission=message['commission'],
        )
        obj.save()

    @transaction.atomic()
    def create_internal_transaction(self, message: dict) -> Order:
        network = Network.objects.get(pk=message['network_id'])

        if message.get('contract_address'):
            currency = network.currencies.get(address=message['contract_address'])
        else:
            currency = network.native_currency

        wallet = InternalWallet.objects.get(address=message['to_address'])

        order = Order.objects.create(
            amount=message['amount'],
            currency=currency,
            user=wallet.user,
            wallet=wallet,
            status=Order.Status.PROCESSED,
        )
        self.create_transaction(message, order=order)
        return order

    @transaction.atomic()
    def create_external_transaction(self, message: dict) -> Order:
        order = Order.objects.get(pk=message['order_id'])
        self.create_transaction(message, order=order)
        order.status = Order.Status.PROCESSED
        order.save()
        return order

    @transaction.atomic()
    def processing_message(self, message: dict):
        if message.get('order_id'):
            return self.create_external_transaction(message)
        else:
            return self.create_internal_transaction(message)

    @transaction.atomic()
    def handle(self, *args, **options):
        for message in self.take_message():
            order = self.processing_message(message)
            self.telegram_notification(order.user, order)
