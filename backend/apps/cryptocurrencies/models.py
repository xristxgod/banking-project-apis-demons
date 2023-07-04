from __future__ import annotations

import decimal

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

    url = models.URLField(_('Node url'), blank=True, null=True)
    block_explorer_url = models.URLField(_('Block explorer url'), blank=True, null=True)
    chain_id = models.IntegerField(_('Chain id'), blank=True, null=True)

    active = models.BooleanField(_('Active'), default=True)

    objects = ActiveManager()

    class Meta:
        verbose_name = _('Network')
        verbose_name_plural = _('Networks')

    @property
    def telegram_view(self) -> str:
        return f'{self.name}'

    @property
    def native_currency(self) -> Currency:
        return self.currencies.get(name=self.name)


class CurrencyFilterManager(ActiveManager):
    def stable_coins(self):
        return self.filter(
            address__isnull=False,
        )

    def by_verbose_telegram(self, currency: str):
        network_name, symbol = currency.split(':')
        return self.filter(
            network__name=network_name,
            symbol=symbol,
        )


class Currency(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    symbol = models.CharField(_('Symbol'), max_length=255)
    decimal_place = models.IntegerField(_('Decimal place'), default=6)
    address = models.CharField(_('Contract address'), max_length=50, blank=True, null=True)

    network = models.ForeignKey(Network, verbose_name=_('Network'), related_name='currencies', on_delete=models.CASCADE)

    coin_gecko_id = models.CharField(_('Coin gecko id'), max_length=25)
    active = models.BooleanField(_('Active'), default=True)

    objects = ActiveManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = decimal.Context(prec=self.decimal_place)

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

    def __str__(self):
        return f'{self.network.name.upper()}:{self.symbol.upper()}'

    @property
    def is_native(self) -> str:
        return self.address is None

    @property
    def abi(self) -> dict:
        return abi.ERC20

    @property
    def verbose_telegram(self) -> str:
        return str(self)


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
