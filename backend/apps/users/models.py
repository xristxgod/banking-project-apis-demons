import decimal

from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class DepositCommissionStatus(models.IntegerChoices):
        PRE_STANDARD = 0, _('Pre standard')     # 15 %
        STANDARD = 1, _('Standard')             # 10 %
        VIP = 2, _('VIP')                       # 5 %
        ADMIN = 3, _('Admin')                   # 1 %
        SUPER_USER = -1, _('Super user')        # 0 %

    class WithdrawCommissionStatus(models.IntegerChoices):
        PRE_STANDARD = 0, _('Pre standard')     # 10 %
        STANDARD = 1, _('Standard')             # 8 %
        VIP = 2, _('VIP')                       # 3 %
        ADMIN = 3, _('Admin')                   # 1 %
        SUPER_USER = -1, _('Super user')        # 0 %

    id = models.BigIntegerField(_('Chat id'), primary_key=True)
    password = models.CharField(_('Password'), max_length=128, blank=True, null=True, default=None)

    deposit_commission_status = models.IntegerField(_('Personal deposit commission'),
                                                    choices=DepositCommissionStatus.choices,
                                                    default=DepositCommissionStatus.PRE_STANDARD)
    withdraw_commission_status = models.IntegerField(_('Personal withdraw commission'),
                                                     choices=WithdrawCommissionStatus.choices,
                                                     default=WithdrawCommissionStatus.PRE_STANDARD)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    @property
    def telegram_username(self) -> str:
        return f'@{self.username}'

    @property
    def deposit_percent(self) -> int:
        from apps.users.utils import deposit_percent
        return deposit_percent(self)

    @property
    def withdraw_percent(self) -> int:
        from apps.users.utils import withdraw_percent
        return withdraw_percent(self)

    @property
    def balance(self) -> decimal.Decimal:
        from apps.users.services import get_balance
        return get_balance(self)

    @property
    def active_deposit(self):
        from apps.users.services import get_active_deposit
        return get_active_deposit(self)

    @property
    def last_deposit(self):
        from apps.users.services import get_last_deposit
        return get_last_deposit(self)

    @property
    def active_withdraw(self):
        from apps.users.services import get_active_withdraw
        return get_active_withdraw(self)

    @property
    def last_withdraw(self):
        from apps.users.services import get_last_withdraw
        return get_last_withdraw(self)
