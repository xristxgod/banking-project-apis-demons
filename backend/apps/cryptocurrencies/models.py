from __future__ import annotations

from django.db import models
from django.utils.translation import gettext as _

from apps.telegram.models import User


class Network(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    chain_id = models.IntegerField(_('Chain id'), blank=True, null=True)
    url = models.URLField(_('Node url'), blank=True, null=True)

    active = models.BooleanField(_('Active Network'), default=True)

    class Meta:
        verbose_name = _('Network')
        verbose_name_plural = _('Networks')

    @property
    def native_currency(self) -> Currency:
        return self.currencies.get(name=self.name)


class Currency(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    symbol = models.CharField(_('Symbol'), max_length=255)
    decimal_place = models.IntegerField(_('Decimal place'), default=6)
    address = models.CharField(_('Contract address'), max_length=50, blank=True, null=True)
    network = models.ForeignKey(Network, verbose_name=_('Network'), related_name='currencies', on_delete=models.CASCADE)

    active = models.BooleanField(_('Active Currency'), default=True)

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

    @classmethod
    def only_stable_coins_qs(cls, active: bool = True):
        return cls.objects.filter(
            address__isnull=False,
            active=True,
        )

    @property
    def verbose_telegram_name(self) -> str:
        # TODO
        return self.symbol

    @property
    def is_native(self) -> str:
        return self.address is None


class Wallet(models.Model):
    address = models.CharField(_('Address'), max_length=255, primary_key=True)
    network = models.ForeignKey(Network, verbose_name=_('Network'), related_name='wallets', on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='wallets', on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')
