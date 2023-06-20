import decimal

from django.db import transaction

from apps.orders.models import Order
from apps.telegram.models import User
from apps.cryptocurrencies.models import Currency


class OrderCreated(Exception):
    pass


@transaction.atomic()
def create_order(user: User, amount: decimal.Decimal, currency: Currency, message_id: int):
    order = Order.objects.create(
        user=user,
        amount=amount,
        currency=currency,
        message_id=message_id,
    )
    return order


def get_payment_receipt_url(order: Order) -> str:
    if order.status != Order.Status.CREATE:
        raise OrderCreated()


def orders_to_excel(user: User) -> str:
    pass


@transaction.atomic()
def update_order(order: Order, status: Order.Status):
    order.status = status
    order.save()
    # TODO update telegram message
