from django.db import models
from django.utils.translation import gettext as _


class User(models.Model):
    id = models.BigIntegerField(_('Chat id'), primary_key=True)
    username = models.CharField(_('Username'), max_length=255)

    created = models.DateTimeField(_('Created'), auto_now=True)

    class Meta:
        verbose_name = _('Telegram user')
        verbose_name_plural = _('Telegram users')


class Balance(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'), primary_key=True,
                                related_name='balance', on_delete=models.CASCADE)
    amount = models.DecimalField(_('Balance'), max_digits=25, decimal_places=25)

    class Meta:
        verbose_name = _('Balance')
        verbose_name_plural = _('Balances')
