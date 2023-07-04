import decimal

from django.db.models import Sum

from src.caches.ram import cached

from apps.users.models import User
from apps.orders.models import OrderStatus, Payment


@cached(60 * 2)
def get_balance(user: User) -> decimal.Decimal:
    deposit = Payment.objects.filter(
        order__user=user,
        order__status=OrderStatus.DONE,
        type__in=[Payment.Type.DEPOSIT, Payment.Type.BY_PROVIDER_DEPOSIT]
    ).aggregate(
        Sum('usdt_amount')
    )

    withdraw = Payment.objects.filter(
        order__user=user,
        order__status=OrderStatus.DONE,
        type=Payment.Type.WITHDRAW
    ).aggregate(
        Sum('usdt_amount')
    )

    balance = deposit['usdt_amount__sum'] - withdraw['usdt_amount__sum']

    with decimal.localcontext() as ctx:
        ctx.prec = 2
        balance = ctx.create_decimal(balance)

    return balance
