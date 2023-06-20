from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.cryptocurrencies.models import Currency
from apps.users.models import User


class OrderFileterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            deleted__isnull=True,
        )

    def expired(self):
        return self.filter(
            created__lt=timezone.now() - timedelta(hours=24 * 30),
            status=OrderStatus.CREATED,
        )


class OrderStatus(models.IntegerChoices):
    CREATED = 0, _('Created')
    CANCEL = 1, _('Cancel')
    SENT = 2, _('Sent')
    PROCESSED = 3, _('Processed')
    DONE = 4, _('Done')
    ERROR = -1, _('Error')


class OrderType(models.TextChoices):
    WITHDRAW = 'withdraw', _('Withdraw')
    DEPOSIT = 'deposit', _('Deposit')


class Order(models.Model):
    amount = models.DecimalField(_('Amount'), max_digits=25, decimal_places=25)
    usd_exchange_rate = models.DecimalField(_('USD rate'), max_digits=25, decimal_places=2)
    commission = models.DecimalField(_('Commission'), max_digits=25, decimal_places=2, default=0)

    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), related_name='orders', on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='orders', on_delete=models.PROTECT)

    status = models.IntegerField(_('Status'), choices=OrderStatus.choices, default=OrderStatus.CREATED)
    type = models.CharField(_('Type'), max_length=50, choices=OrderType.choices, default=OrderType.DEPOSIT)

    created = models.DateTimeField(_('Created'), auto_now=True)
    updated = models.DateTimeField(_('Updated'), auto_now_add=True)
    deleted = models.DateTimeField(_('Deleted'), blank=True, null=True, default=None)

    message_id = models.IntegerField(_('Telegram message id'), blank=True, null=True, default=None)

    objects = OrderFileterManager()

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    @property
    def is_done(self) -> bool:
        return self.status == OrderStatus.DONE

    @property
    def verbose_currency(self):
        if self.currency.is_native:
            return f'{self.currency.symbol}'
        return f'{self.currency.network.name}:{self.currency.symbol}'


class Transaction(models.Model):
    order = models.OneToOneField(Order, verbose_name=_('Order'), primary_key=True, related_name='transaction',
                                 on_delete=models.PROTECT)
    transaction_hash = models.CharField(_('Transaction hash'), max_length=255)
    timestamp = models.IntegerField(_('Timestamp'))

    sender_address = models.CharField(_('Sender address'), max_length=255)
    recipient_address = models.CharField(_('Recipient address'), max_length=255)

    fee = models.DecimalField(_('Commission'), max_digits=25, decimal_places=25, default=0)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')

    @property
    def hash(self) -> str:
        return self.transaction_hash
