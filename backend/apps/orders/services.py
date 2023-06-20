from django.db import transaction

from apps.orders.models import OrderStatus, Order


@transaction.atomic()
def order_sent(order: Order):
    order.status = OrderStatus.SENT
    order.save()

    if order.message_id:
        # TODO edit a message in a telegram
        pass

    return order
