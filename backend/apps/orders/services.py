import decimal

from django.db import transaction

from apps.cryptocurrencies.clients import crypto_exchange_client
from apps.cryptocurrencies.services import generate_temp_wallet

from apps.users.models import User
from apps.cryptocurrencies.models import Currency

from apps.orders import models


def calculate_deposit_amount(user: User, amount: decimal.Decimal, currency: Currency) -> dict:
    usdt_info = crypto_exchange_client.get_currency_to_usdt_rate(currency)

    with decimal.localcontext() as ctx:
        ctx.prec = 99
        usdt_amount_without_commission = decimal.Decimal(amount * usdt_info['price'], context=ctx)
        usdt_commission = decimal.Decimal(usdt_amount_without_commission / 100 * user.deposit_percent, context=ctx)
        usdt_amount = decimal.Decimal(usdt_amount_without_commission - usdt_commission, context=ctx)

    return dict(
        usdt_info=usdt_info,
        usdt_amount_without_commission=round(usdt_amount_without_commission, 2),
        usdt_amount=round(usdt_amount, 2),
        usdt_commission=round(usdt_commission, 2),
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
    if status == models.OrderStatus.CANCEL:
        return cancel_payment(payment)
    return payment.update_status(status)


@transaction.atomic()
def cancel_payment(payment: models.Payment) -> models.Payment:
    return payment.make_cancel()
