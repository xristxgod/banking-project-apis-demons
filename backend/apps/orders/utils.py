from apps.orders.models import Order


def encode_token(order: Order) -> str:
    # TODO
    return str(order.pk)


def decode_token(token: str) -> int:
    # TODO
    return int(token)
