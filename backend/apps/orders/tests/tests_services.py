import time
import decimal

import pytest

from apps.users.models import User
from apps.users.tests.factories import UserFactory
from apps.cryptocurrencies.tests.factories import CurrencyFactory


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
