from __future__ import annotations

from django.db import models
from django.utils.translation import gettext as _

from apps.cryptocurrencies import abi


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().select_related().filter(
            active=True,
        )


class Network(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    chain_id = models.IntegerField(_('Chain id'), blank=True, null=True)
    url = models.URLField(_('Node url'), blank=True, null=True)
    active = models.BooleanField(_('Active'), default=True)

    objects = ActiveManager()

    class Meta:
        verbose_name = _('Network')
        verbose_name_plural = _('Networks')

    @property
    def native_currency(self) -> Currency:
        return self.currencies.get(name=self.name)


class CurrencyFilterManager(ActiveManager):
    def stable_coins(self):
        return self.filter(
            address__isnull=False,
        )


class Currency(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    symbol = models.CharField(_('Symbol'), max_length=255)
    decimal_place = models.IntegerField(_('Decimal place'), default=6)
    address = models.CharField(_('Contract address'), max_length=50, blank=True, null=True)
    network = models.ForeignKey(Network, verbose_name=_('Network'), related_name='currencies', on_delete=models.CASCADE)
    active = models.BooleanField(_('Active'), default=True)

    objects = ActiveManager()

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

    @property
    def is_native(self) -> str:
        return self.address is None

    @property
    def abi(self) -> dict:
        return abi.ERC20


class Provider(models.Model):
    network = models.OneToOneField(Network, verbose_name=_('Network'), related_name='provider',
                                   on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(_('Contract address'), max_length=255)

    class Meta:
        verbose_name = _('Provider')
        verbose_name_plural = _('Providers')

    @property
    def abi(self) -> dict:
        return abi.PROVIDER
