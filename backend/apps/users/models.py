from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class DepositCommissionPercent(models.IntegerChoices):
        PRE_STANDARD = 0, _('Pre standard')     # 15 %
        STANDARD = 1, _('Standard')             # 10 %
        VIP = 2, _('VIP')                       # 5 %
        ADMIN = 3, _('Admin')                   # 1 %
        SUPER_USER = -1, _('Super user')        # 0 %

    class WithdrawCommissionPercent(models.IntegerChoices):
        PRE_STANDARD = 0, _('Pre standard')     # 10 %
        STANDARD = 1, _('Standard')             # 8 %
        VIP = 2, _('VIP')                       # 3 %
        ADMIN = 3, _('Admin')                   # 1 %
        SUPER_USER = -1, _('Super user')        # 0 %

    id = models.BigIntegerField(_('Chat id'), primary_key=True)
    password = models.CharField(_('Password'), max_length=128, blank=True, null=True, default=None)

    deposit_commission_percent = models.IntegerField(_('Personal deposit commission'),
                                                     choices=DepositCommissionPercent.choices,
                                                     default=DepositCommissionPercent.PRE_STANDARD)
    withdraw_commission_percent = models.IntegerField(_('Personal withdraw commission'),
                                                      choices=WithdrawCommissionPercent.choices,
                                                      default=WithdrawCommissionPercent.PRE_STANDARD)

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
