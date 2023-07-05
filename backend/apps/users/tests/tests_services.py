import pytest

from .factories import UserFactory

from apps.users.services import get_balance


@pytest.mark.django_db
def test_get_balance():
    from apps.orders.models import Payment
    from apps.orders.tests.factories import PaymentFactory

    user = UserFactory()

    deposit = PaymentFactory(type=Payment.Type.DEPOSIT, is_done=True, order__user=user)
    by_provider_deposit = PaymentFactory(type=Payment.Type.BY_PROVIDER_DEPOSIT, is_done=True, order__user=user)
    withdraw = PaymentFactory(type=Payment.Type.WITHDRAW, is_done=True, order__user=user)

    balance = deposit.usdt_amount + by_provider_deposit.usdt_amount - withdraw.usdt_amount

    assert balance.compare(get_balance(user))
