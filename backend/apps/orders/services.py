import decimal

from django.db import transaction

from apps.orders.models import Order
from apps.telegram.models import User
from apps.cryptocurrencies.models import Currency


@transaction.atomic()
def create_order(user: User, amount: decimal.Decimal, currency: Currency, message_id: int):
    order = Order.objects.create(
        user=user,
        amount=amount,
        currency=currency,
        message_id=message_id,
    )
    return order


@transaction.atomic()
def update_order(order: Order, status: Order.Status):
    order.status = status
    order.save()
