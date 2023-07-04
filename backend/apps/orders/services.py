import decimal

from django.db import transaction

from apps.cryptocurrencies.clients import coin_gecko_client
from apps.cryptocurrencies.services import generate_temp_wallet

from apps.users.models import User
from apps.cryptocurrencies.models import Currency

from apps.orders import models


def calculate_deposit_amount(user: User, amount: decimal.Decimal, currency: Currency) -> dict:
    usdt_info = coin_gecko_client.get_currency_to_usdt_rate(currency)

    with decimal.localcontext() as ctx:
        ctx.prec = 8
        usdt_amount_without_commission = ctx.create_decimal(amount / usdt_info['price'])
        usdt_commission = ctx.create_decimal(usdt_amount_without_commission / 100 * user.deposit_percent)
        usdt_amount = ctx.create_decimal(usdt_amount_without_commission - usdt_commission)

    usdt_amount_without_commission = decimal.Decimal(amount / usdt_info['price'])

    return dict(
        usdt_info=usdt_info,
        usdt_amount_without_commission=usdt_amount_without_commission,
        usdt_amount=usdt_amount,
        usdt_commission=usdt_commission,
    )


@transaction.atomic()
def create_payment(user: User, typ: models.Payment.Type, **params):
    order = models.Order.objects.create(
        user=user,
        amount=params['amount'],
        currency=params['currency'],
    )

    payment = models.Payment.objects.create(
        order=order,
        type=typ,
        usdt_amount=params['usdt_amount'],
        usdt_exchange_rate=params['usdt_exchange_rate'],
        usdt_commission=params['usdt_commission'],
    )

    if typ == models.Payment.Type.DEPOSIT:
        models.TempWallet.objects.create(
            deposit=payment,
            **generate_temp_wallet(currency=params['currency']),
        )

    return payment


@transaction.atomic()
def update_payment_status(payment: models.Payment, status: models.OrderStatus) -> models.Payment:
    return payment.update_status(status)


@transaction.atomic()
def cancel_payment(payment: models.Payment) -> models.Payment:
    return payment.make_cancel()
