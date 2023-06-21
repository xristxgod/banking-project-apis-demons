from django.db import transaction

from apps.orders.models import OrderStatus, Order


@transaction.atomic()
def order_update_status(order: Order, status: OrderStatus):
    order.status = status
    order.save()

    if order.message_id:
        # TODO edit a message in a telegram
        pass

    return order
