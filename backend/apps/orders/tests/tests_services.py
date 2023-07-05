import time
import decimal

import pytest

from apps.users.models import User
from apps.users.tests.factories import UserFactory
from apps.cryptocurrencies.tests.factories import CurrencyFactory

from apps.orders import models

from .factories import fake
from .factories import OrderFactory, PaymentFactory


@pytest.mark.django_db
@pytest.mark.parametrize('deposit_commission_status, amount, usdt_price, result', [
    # TRX
    (User.DepositCommissionStatus.PRE_STANDARD, decimal.Decimal(17), decimal.Decimal(repr(0.077)), {
        'usdt_amount_without_commission': decimal.Decimal('1.31'),
        'usdt_amount': decimal.Decimal('1.11'),
        'usdt_commission': decimal.Decimal('0.20'),
    }),
    # ETH
    (User.DepositCommissionStatus.STANDARD, decimal.Decimal(0.2), decimal.Decimal(repr(1912.43)), {
        'usdt_amount_without_commission': decimal.Decimal('382.49'),
        'usdt_amount': decimal.Decimal('344.24'),
        'usdt_commission': decimal.Decimal('38.25'),
    }),
    # BSC
    (User.DepositCommissionStatus.VIP, decimal.Decimal(12.25), decimal.Decimal(repr(238.25)), {
        'usdt_amount_without_commission': decimal.Decimal('2918.56'),
        'usdt_amount': decimal.Decimal('2772.63'),
        'usdt_commission': decimal.Decimal('145.93'),
    }),
    # LINK
    (User.DepositCommissionStatus.ADMIN, decimal.Decimal(2.4235), decimal.Decimal(repr(6.32)), {
        'usdt_amount_without_commission': decimal.Decimal('15.32'),
        'usdt_amount': decimal.Decimal('15.16'),
        'usdt_commission': decimal.Decimal('0.15'),
    }),
    # DNC
    (User.DepositCommissionStatus.SUPER_USER, decimal.Decimal(55.5123), decimal.Decimal(repr(0.205976)), {
        'usdt_amount_without_commission': decimal.Decimal('11.43'),
        'usdt_amount': decimal.Decimal('11.43'),
        'usdt_commission': decimal.Decimal('0.00'),
    }),
])
def test_calculate_deposit_amount(deposit_commission_status, amount, usdt_price, result, mocker):
    from apps.orders.services import calculate_deposit_amount

    currency = CurrencyFactory()
    user = UserFactory(
        deposit_commission_status=deposit_commission_status,
    )

    usdt_info = {
        'price': usdt_price,
        'last_updated_at': time.time_ns(),
    }
    result.update(dict(usdt_info=usdt_info))

    mocker.patch(
        'apps.orders.services.coin_gecko_client.get_currency_to_usdt_rate',
        return_value=usdt_info,
    )

    response = calculate_deposit_amount(
        user=user,
        amount=amount,
        currency=currency,
    )

    assert response == result


@pytest.mark.django_db
@pytest.mark.parametrize('typ', [
    models.Payment.Type.DEPOSIT,
    models.Payment.Type.BY_PROVIDER_DEPOSIT,
    models.Payment.Type.WITHDRAW,
])
def test_create_payment(typ):
    from apps.orders.services import create_payment

    user = UserFactory()
    currency = CurrencyFactory()

    params = {
        'amount': fake.unique.pydecimal(left_digits=1, right_digits=4, positive=True),
        'currency': currency,
        'usdt_amount': fake.unique.pydecimal(left_digits=2, right_digits=2, positive=True),
        'usdt_exchange_rate': fake.unique.pydecimal(left_digits=2, right_digits=2, positive=True),
        'usdt_commission': fake.unique.pydecimal(left_digits=2, right_digits=2, positive=True),
    }

    payment = create_payment(user, typ, **params)

    assert payment.order.amount == params['amount']
    assert payment.order.currency == currency
    assert payment.usdt_amount == params['usdt_amount']
    assert payment.usdt_exchange_rate == params['usdt_exchange_rate']
    assert payment.usdt_commission == params['usdt_commission']

    assert payment.status == models.OrderStatus.CREATED

    if typ == models.Payment.Type.DEPOSIT:
        assert hasattr(payment, 'temp_wallet')


@pytest.mark.django_db
def test_update_and_cancel_payment():
    from apps.orders.services import update_payment_status, cancel_payment

    order1 = OrderFactory(status=models.OrderStatus.CREATED)
    payment1 = PaymentFactory(order=order1)

    assert payment1.status == models.OrderStatus.CREATED

    cancel_payment(payment1)

    qs = models.Payment.objects.filter(pk=payment1.pk)

    assert qs.first().status == models.OrderStatus.CANCEL

    update_payment_status(qs.first(), models.OrderStatus.DONE)

    assert (
            qs.first().status != models.OrderStatus.DONE and
            qs.first().status == models.OrderStatus.CANCEL
    )

    order2 = OrderFactory(status=models.OrderStatus.CREATED)
    payment2 = PaymentFactory(order=order2)

    update_payment_status(payment2, models.OrderStatus.DONE)

    qs = models.Payment.objects.filter(pk=payment2.pk)

    assert qs.first().status == models.OrderStatus.DONE

    cancel_payment(qs.first())

    assert (
            qs.first().status == models.OrderStatus.DONE and
            qs.first().status != models.OrderStatus.CANCEL
    )
