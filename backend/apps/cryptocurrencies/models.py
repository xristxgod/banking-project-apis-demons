from __future__ import annotations

from django.db import models
from django.utils.translation import gettext as _

from apps.telegram.models import User


class Network(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    chain_id = models.IntegerField(_('Chain id'), blank=True, null=True)

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

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

    @property
    def is_native(self) -> str:
        return self.address is None


class AbstractWallet(models.Model):
    address = models.CharField(_('Address'), max_length=255, primary_key=True)
    network = models.ForeignKey(Network, verbose_name=_('Network'), related_name='external_wallet',
                                on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='external_wallet',
                             on_delete=models.PROTECT)

    class Meta:
        abstract = True

    @property
    def wallet_type(self) -> str:
        raise NotImplementedError()


class ExternalWallet(AbstractWallet):
    class Type(models.TextChoices):
        METAMASK = 'metamask', 'Metamask'

    signature = models.CharField(_('Signature'), max_length=50)
    type = models.CharField(_('Type'), choices=Type.choices, default=Type.METAMASK)

    class Meta:
        verbose_name = _('External wallet')
        verbose_name_plural = _('External wallets')

    @property
    def wallet_type(self) -> str:
        return 'external'


class InternalWallet(AbstractWallet):
    private_key = models.CharField(_('Private key'), max_length=255)

    class Meta:
        verbose_name = _('Internal wallet')
        verbose_name_plural = _('Internal wallets')

    @property
    def wallet_type(self) -> str:
        return 'internal'

    @property
    def qr(self):
        # TODO Add generate QR core by address
        raise NotImplementedError()
