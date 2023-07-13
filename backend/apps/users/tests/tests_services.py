import pytest

from apps.orders.models import OrderStatus, Payment
from apps.orders.tests.factories import PaymentFactory

from .factories import UserFactory


@pytest.mark.django_db
def test_get_balance():
    from apps.users.services import get_balance
    from apps.orders.tests.factories import PaymentFactory

    user = UserFactory()

    deposit = PaymentFactory(type=Payment.Type.DEPOSIT, is_done=True, order__user=user)
    by_provider_deposit = PaymentFactory(type=Payment.Type.BY_PROVIDER_DEPOSIT, is_done=True, order__user=user)
    withdraw = PaymentFactory(type=Payment.Type.WITHDRAW, is_done=True, order__user=user)

    balance = deposit.usdt_amount + by_provider_deposit.usdt_amount - withdraw.usdt_amount

    assert balance.compare(get_balance(user))


@pytest.mark.django_db
class TestUserPayment:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = UserFactory()

    @pytest.mark.parametrize('typ', [
        Payment.Type.DEPOSIT,
        Payment.Type.BY_PROVIDER_DEPOSIT,
    ])
    def test_deposit(self, typ):
        from apps.users.services import get_active_deposit, get_last_deposit

        deposit1 = PaymentFactory(type=typ, order__user=self.user, is_created=True)

        assert get_active_deposit(self.user) == deposit1
        assert get_last_deposit(self.user) == deposit1

        deposit1.update_status(OrderStatus.DONE)

        assert get_active_deposit(self.user) is None
        assert get_last_deposit(self.user) == deposit1

        deposit2 = PaymentFactory(type=typ, order__user=self.user, is_created=True)

        assert get_active_deposit(self.user) == deposit2
        assert get_last_deposit(self.user) == deposit1

        deposit2.update_status(OrderStatus.DONE)

        assert get_active_deposit(self.user) is None
        assert get_last_deposit(self.user) == deposit2

    def test_deposit_history(self):
        from apps.users.services import get_deposit_history

        _ = PaymentFactory(type=Payment.Type.DEPOSIT, order__user=self.user, is_created=True)
        _ = PaymentFactory(type=Payment.Type.DEPOSIT, order__user=self.user, is_created=True)

        withdraw = PaymentFactory(type=Payment.Type.WITHDRAW, order__user=self.user, is_done=True)
        deposit3 = PaymentFactory(type=Payment.Type.DEPOSIT, order__user=self.user, is_cancel=True)
        deposit4 = PaymentFactory(type=Payment.Type.BY_PROVIDER_DEPOSIT, order__user=self.user, is_done=True)
        deposit5 = PaymentFactory(type=Payment.Type.DEPOSIT, order__user=self.user, is_done=True)

        history = get_deposit_history(self.user)

        assert len(history) == 3
        assert list(history) == [deposit3, deposit4, deposit5]

    def test_withdraw(self):
        from apps.users.services import get_active_withdraw, get_last_withdraw

        withdraw1 = PaymentFactory(type=Payment.Type.WITHDRAW, order__user=self.user, is_created=True)

        assert get_active_withdraw(self.user) == withdraw1
        assert get_last_withdraw(self.user) == withdraw1

        withdraw1.update_status(OrderStatus.DONE)

        assert get_active_withdraw(self.user) is None
        assert get_last_withdraw(self.user) == withdraw1

        withdraw2 = PaymentFactory(type=Payment.Type.WITHDRAW, order__user=self.user, is_created=True)

        assert get_active_withdraw(self.user) == withdraw2
        assert get_last_withdraw(self.user) == withdraw1

        withdraw2.update_status(OrderStatus.DONE)

        assert get_active_withdraw(self.user) is None
        assert get_last_withdraw(self.user) == withdraw2

    def test_withdraw_history(self):
        from apps.users.services import get_withdraw_history

        _ = PaymentFactory(type=Payment.Type.WITHDRAW, order__user=self.user, is_created=True)
        _ = PaymentFactory(type=Payment.Type.WITHDRAW, order__user=self.user, is_created=True)

        deposit = PaymentFactory(type=Payment.Type.DEPOSIT, order__user=self.user, is_done=True)
        withdraw3 = PaymentFactory(type=Payment.Type.WITHDRAW, order__user=self.user, is_cancel=True)
        withdraw4 = PaymentFactory(type=Payment.Type.WITHDRAW, order__user=self.user, is_done=True)
        withdraw5 = PaymentFactory(type=Payment.Type.WITHDRAW, order__user=self.user, is_done=True)

        history = get_withdraw_history(self.user)

        assert len(history) == 3
        assert list(history) == [withdraw3, withdraw4, withdraw5]