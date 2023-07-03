import decimal

from django.db import transaction

from apps.users.models import User
from apps.orders.models import Deposit, Order
from apps.cryptocurrencies.models import Currency


def get_usdt_rate_cost(currency: Currency) -> decimal.Decimal:
    # FIXME
    amount_in_resp = round(1.2, 2)
    return decimal.Decimal(repr(amount_in_resp))


def calculate_deposit_amount(user: User, amount: decimal.Decimal, currency: Currency) -> dict:
    usd_rate_cost = get_usdt_rate_cost(currency)

    usdt_amount_without_commission = round(amount / usd_rate_cost, 2)
    usdt_commission = round(usdt_amount_without_commission / 100 * user.personal_commission_percent, 2)
    usdt_amount = round(usdt_amount_without_commission - usdt_commission, 2)

    return dict(
        usdt_rate_cost=usd_rate_cost,
        usdt_amount=usdt_amount,
        usdt_commission=usdt_commission,
    )


@transaction.atomic()
def create_deposit(user: User, deposit_info: dict) -> Deposit:
    order = Order.objects.create(
        user=user,
        amount=deposit_info['amount'],
        currency=deposit_info['currency'],
    )
    return Deposit.objects.create(
        order=order,
        usdt_amount=deposit_info['usdt_amount'],
        usdt_exchange_rate=deposit_info['usdt_rate_cost'],
        usdt_commission=deposit_info['usdt_commission'],
    )


@transaction.atomic()
def cancel_deposit(deposit: Deposit) -> Deposit:
    return deposit.make_cancel()
