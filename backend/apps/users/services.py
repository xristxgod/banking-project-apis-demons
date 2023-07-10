import decimal
from typing import Optional

from django.db.models import Sum, Q

from src.caches.ram import cached

from apps.users.models import User
from apps.orders.models import OrderStatus, Order, Payment


@cached(60 * 2)
def get_balance(user: User) -> decimal.Decimal:
    deposit_sum = Payment.objects.filter(
        order__user=user,
        order__status=OrderStatus.DONE,
        type__in=[Payment.Type.DEPOSIT, Payment.Type.BY_PROVIDER_DEPOSIT]
    ).aggregate(
        Sum('usdt_amount', default=0)
    )

    withdraw_sum = Payment.objects.filter(
        order__user=user,
        order__status=OrderStatus.DONE,
        type=Payment.Type.WITHDRAW
    ).aggregate(
        Sum('usdt_amount', default=0)
    )

    balance = deposit_sum['usdt_amount__sum'] - withdraw_sum['usdt_amount__sum']

    with decimal.localcontext() as ctx:
        ctx.prec = 2
        balance = ctx.create_decimal(balance)

    return balance


@cached(60 * 2)
def get_active_deposit(user: User) -> Optional[Payment]:
    return Payment.objects.filter(
        order__user=user,
        order__status=OrderStatus.CREATED,
        type__in=(Payment.Type.DEPOSIT, Payment.Type.BY_PROVIDER_DEPOSIT)
    ).first()


@cached(60 * 2)
def get_last_deposit(user: User) -> Optional[Payment]:
    obj = Payment.objects.filter(
        order__user=user,
        order__status__in=(*Order.DONE_STATUSES, OrderStatus.SENT),
        type__in=[Payment.Type.DEPOSIT, Payment.Type.BY_PROVIDER_DEPOSIT],
    ).order_by(
        'order__confirmed'
    ).last()

    if not obj:
        obj = get_active_deposit(user)

    return obj


@cached(60 * 2)
def get_active_withdraw(user: User) -> Optional[Payment]:
    return Payment.objects.filter(
        order__user=user,
        type=Payment.Type.WITHDRAW,
    ).filter(
        ~Q(order__status__in=Order.DONE_STATUSES)
    ).first()


@cached(60 * 2)
def get_last_withdraw(user: User) -> Optional[Payment]:
    obj = Payment.objects.filter(
        order__user=user,
        order__status__in=Order.DONE_STATUSES,
        type=Payment.Type.WITHDRAW,
    ).order_by(
        'order__confirmed'
    ).last()

    if not obj:
        obj = get_active_withdraw(user)

    return obj
