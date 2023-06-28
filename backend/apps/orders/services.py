import decimal

from django.db import transaction

from apps.users.models import User
from apps.orders.models import Deposit, Order
from apps.cryptocurrencies.models import Currency


def get_usd_rate(currency: Currency) -> decimal.Decimal:
    # FIXME
    with decimal.localcontext() as ctx:
        return decimal.Decimal(10, context=ctx)


def calculate_deposit_amount(user: User, amount: decimal.Decimal, currency: Currency) -> dict:
    with decimal.localcontext() as ctx:
        ctx.prec = 2
        usd_rate = get_usd_rate(currency)
        amount = decimal.Decimal(amount / usd_rate, context=ctx)
        commission = decimal.Decimal(amount / 100 * user.personal_commission_percent, context=ctx)
        amount = decimal.Decimal(amount - commission, context=ctx)

    return {
        'usd_rate': usd_rate,
        'usd_amount': amount,
        'usd_commission': commission,
    }


@transaction.atomic()
def create_deposit_by_telegram(user: User, deposit_info: dict) -> Deposit:
    order = Order.objects.create(
        amount=deposit_info['amount'],
        currency=deposit_info['currency'],
        user=user,
    )
    deposit = Deposit.objects.create(
        order=order,
        amount=deposit_info['usd_amount'],
        usd_exchange_rate=deposit_info['usd_rate'],
        commission=deposit_info['usd_commission'],
    )

    return deposit


@transaction.atomic()
def cancel_deposit(user: User, pk: int):
    deposit = Deposit.objects.get(
        order__user=user,
        pk=pk,
    )
    deposit.make_cancel()
