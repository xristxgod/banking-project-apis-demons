import decimal

from django.db.models import Sum

from apps.users.models import User
from apps.orders.models import OrderStatus, Deposit


def get_balance(user: User) -> decimal.Decimal:
    balance = 0

    deposits_amount = Deposit.objects.filter(
        order__user=user,
        order__status=OrderStatus.DONE,
    ).aggregate(
        Sum('amount')
    )

    balance += deposits_amount

    with decimal.localcontext() as ctx:
        ctx.prec = 2
        balance = ctx.create_decimal(balance)

    return balance
