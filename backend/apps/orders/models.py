from urllib.parse import urljoin

from django.utils import timezone
from django.db import models, transaction
from django.utils.translation import gettext as _

from apps.cryptocurrencies.models import Currency
from apps.users.models import User


class OrderStatus(models.IntegerChoices):
    CREATED = 0, _('Created')
    CANCEL = 1, _('Cancel')
    SENT = 2, _('Sent')
    DONE = 3, _('Done')
    ERROR = -1, _('Error')


class Order(models.Model):
    amount = models.DecimalField(_('Amount'), max_digits=25, decimal_places=18)

    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), related_name='orders', on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='orders', on_delete=models.PROTECT)

    status = models.IntegerField(_('Status'), choices=OrderStatus.choices, default=OrderStatus.CREATED)

    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    confirmed = models.DateTimeField(_('Confirmed'), blank=True, null=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    @transaction.atomic()
    def make_cancel(self):
        self.status = OrderStatus.CANCEL
        self.confirmed = timezone.now()
        self.save()
        return self

    @transaction.atomic()
    def update_status(self, status: OrderStatus):
        self.status = status
        if self.status == OrderStatus.DONE:
            self.confirmed = timezone.now()
        self.save()
        return self

    @property
    def can_send(self) -> bool:
        return self.status == OrderStatus.CREATED

    @property
    def is_done(self) -> bool:
        return self.confirmed is not None

    @property
    def status_by_telegram(self) -> str:
        match self.status:
            case OrderStatus.CREATED:
                prefix = ':white_circle: '
            case OrderStatus.SENT:
                prefix = ':yellow_circle: '
            case OrderStatus.DONE:
                prefix = ':green_circle: '
            case _:
                prefix = ':red_circle: '
        return prefix + self.get_status_display()


class Transaction(models.Model):
    order = models.OneToOneField(Order, verbose_name=_('Order'), primary_key=True, related_name='transaction',
                                 on_delete=models.PROTECT)
    transaction_hash = models.CharField(_('Transaction hash'), max_length=255)
    timestamp = models.IntegerField(_('Timestamp'))

    sender_address = models.CharField(_('Sender address'), max_length=255)
    recipient_address = models.CharField(_('Recipient address'), max_length=255)

    fee = models.DecimalField(_('Commission'), max_digits=25, decimal_places=18, default=0)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')

    @property
    def hash(self) -> str:
        return self.transaction_hash

    @property
    def url(self) -> str:
        return urljoin(self.order.currency.network.block_explorer_url, self.hash)


class Payment(models.Model):
    class Type(models.TextChoices):
        BY_PROVIDER_DEPOSIT = 'by_provider_deposit', _('By provider deposit')
        DEPOSIT = 'deposit', _('Deposit')
        WITHDRAW = 'withdraw', _('Withdraw')

    order = models.OneToOneField(Order, verbose_name=_('Order'), primary_key=True, related_name='payment',
                                 on_delete=models.PROTECT)
    usdt_amount = models.DecimalField(_('USDT amount'), default=0, max_digits=25, decimal_places=2)
    usdt_exchange_rate = models.DecimalField(_('USDT rate'), default=0, max_digits=25, decimal_places=2)
    usdt_commission = models.DecimalField(_('USDT commission'), default=0, max_digits=25, decimal_places=2)
    type = models.CharField(_('Type'), max_length=255, choices=Type.choices)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    @transaction.atomic()
    def make_cancel(self):
        if self.order.status == OrderStatus.CREATED:
            self.order.make_cancel()
        return self

    @transaction.atomic()
    def update_status(self, status: OrderStatus):
        if not self.order.is_done:
            self.order.update_status(status)
        return self

    @property
    def consumer(self) -> User:
        return self.order.user

    @property
    def create(self):
        return self.order.created

    @property
    def update(self):
        return self.order.updated

    @property
    def confirmed(self):
        return self.order.confirmed

    @property
    def status(self) -> OrderStatus:
        return self.order.status

    @property
    def transaction_url(self) -> str:
        return self.order.transaction.url

    @property
    def url(self) -> str:
        return ''


class TempWallet(models.Model):
    """Temp wallet for deposit"""
    deposit = models.OneToOneField(Payment, verbose_name=_('Deposit'), primary_key=True, related_name='temp_wallet',
                                   on_delete=models.PROTECT)
    address = models.CharField(_('Address'), max_length=255)
    private_key = models.CharField(_('Private key'), max_length=255)

    class Meta:
        verbose_name = _('Temp wallet')
        verbose_name_plural = _('Temp wallets')
