import decimal
from datetime import timedelta

from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone

from apps.telegram.models import User
from apps.cryptocurrencies.models import Currency, ExternalWallet, InternalWallet, AbstractWallet


class Order(models.Model):
    class Status(models.IntegerChoices):
        CREATE = 0, _('Create')
        SENT = 1, _('Sent')
        PROCESSED = 2, _('Processed')
        DONE = 3, _('Done')
        ERROR = -1, _('Error')

    amount = models.DecimalField(_('Amount'), max_digits=25, decimal_places=25)
    currency = models.ForeignKey(Currency, _('Currency'), related_name='orders', on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='orders',
                             on_delete=models.PROTECT)
    wallet = models.ForeignKey(ExternalWallet, verbose_name=_('External Wallet'), related_name='orders',
                               on_delete=models.PROTECT, blank=True, null=True)

    status = models.IntegerField(_('Status'), choices=Status.choices, default=Status.CREATE)

    created = models.DateTimeField(_('Created'), auto_now=True)
    updated = models.DateTimeField(_('Updated'), auto_now_add=True)

    lifetime = timedelta(hours=24*30)

    class Meta:
        verbose_name = _('Internal wallet')
        verbose_name_plural = _('Internal wallets')

    @property
    def expires(self):
        return self.created + self.lifetime

    @property
    def is_expired(self):
        return timezone.now() > self.expires

    @classmethod
    def expired_qs(cls):
        return cls.objects.filter(created__lt=timezone.now() - cls.lifetime, status=cls.Status.CREATE)

    @property
    def is_external(self) -> bool:
        return self.wallet is not None


class Transaction(models.Model):
    order = models.OneToOneField(Order, verbose_name=_('Order'), primary_key=True,
                                 related_name='transaction', on_delete=models.PROTECT)
    transaction_hash = models.CharField(_('Transaction hash'), max_length=255)
    timestamp = models.CharField(_('Timestamp'))

    sender_address = models.CharField(_('Sender address'), max_length=255)
    to_address = models.CharField(_('To address'), max_length=255)

    commission = models.DecimalField(_('Commission'), max_digits=25, decimal_places=25)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transaction')

    @property
    def user(self) -> User:
        return self.order.user

    @property
    def currency(self) -> Currency:
        return self.order.currency

    @property
    def wallet(self) -> AbstractWallet:
        if self.order.is_external:
            return self.order.wallet

        return InternalWallet.objects.get(pk=self.to_address)

    @property
    def is_external(self) -> bool:
        return self.order.is_external


class UserDeposit(models.Model):
    order = models.OneToOneField(Order, verbose_name=_('Order'), primary_key=True,
                                 related_name='user_deposit', on_delete=models.PROTECT)

    amount = models.DecimalField(_('Amount'), max_digits=25, decimal_places=2)
    commission = models.DecimalField(_('Commission'), max_length=25, decimal_places=2)

    created = models.DateTimeField(_('Created'), auto_now=True)

    class Meta:
        verbose_name = _('User deposit')
        verbose_name_plural = _('User deposit')

    service_commission = commission                         # alias

    @property
    def transaction_commission(self) -> decimal.Decimal:
        return self.order.transaction.commission

    @property
    def verbose_transaction_commission(self) -> str:
        return f'{self.transaction_commission} {self.order.currency.symbol}'

    @property
    def verbose_service_commission(self) -> str:
        return f'${self.service_commission}'

    verbose_commission = verbose_service_commission         # alias

    @property
    def verbose_amount(self) -> str:
        return f'${self.amount}'


class ConvertTransactionAmount(models.Model):
    usd_exchange_rate = models.DecimalField(_('Amount'), max_digits=25, decimal_places=2)
    deposit = models.OneToOneField(UserDeposit, verbose_name=_('Order'),
                                   related_name='user_deposit', on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Convert transaction amount')
        verbose_name_plural = _('Convert transaction amounts')
