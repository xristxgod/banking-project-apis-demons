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

    @property
    def can_send(self) -> bool:
        return self.status == OrderStatus.CREATED

    @transaction.atomic()
    def make_cancel(self):
        self.status = OrderStatus.CANCEL
        self.save()

    @property
    def is_done(self) -> bool:
        return self.status in [OrderStatus.DONE, OrderStatus.ERROR]

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


class AbstractPayment(models.Model):
    order = models.OneToOneField(Order, verbose_name=_('Order'), primary_key=True, related_name='deposit',
                                 on_delete=models.PROTECT)
    usdt_amount = models.DecimalField(_('USDT amount'), default=0, max_digits=25, decimal_places=2)
    usdt_exchange_rate = models.DecimalField(_('USDT rate'), default=0, max_digits=25, decimal_places=2)
    usdt_commission = models.DecimalField(_('USDT commission'), default=0, max_digits=25, decimal_places=2)

    class Meta:
        abstract = True

    @transaction.atomic()
    def make_cancel(self):
        if self.order.status == OrderStatus.CREATED:
            self.order.make_cancel()
            self.save()
        return self

    @property
    def consumer(self) -> User:
        return self.order.user

    @property
    def status(self) -> OrderStatus:
        # Proxy
        return self.order.status

    def get_status_display(self) -> str:
        return self.order.get_status_display()

    @property
    def status_by_telegram(self) -> str:
        # Proxy
        return self.order.status_by_telegram

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
    def transaction_url(self) -> str:
        url = self.order.currency.network.block_explorer_url
        return f'{url}/{self.order.transaction.transaction_hash}'


class Deposit(AbstractPayment):

    class Meta:
        verbose_name = _('Deposit')
        verbose_name_plural = _('Deposits')

    @property
    def payment_url(self) -> str:
        # TODO add payment deposit
        return f'https://ru.stackoverflow.com/questions/{self.order.pk}'
