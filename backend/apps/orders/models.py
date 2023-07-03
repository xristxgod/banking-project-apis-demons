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
        return self.status == OrderStatus.DONE

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


class Deposit(models.Model):
    order = models.OneToOneField(Order, verbose_name=_('Order'), primary_key=True, related_name='deposit',
                                 on_delete=models.PROTECT)
    amount = models.DecimalField(_('USD amount'), max_digits=25, decimal_places=2)
    usd_exchange_rate = models.DecimalField(_('USD rate'), max_digits=25, decimal_places=2)
    commission = models.DecimalField(_('USD commission'), max_digits=25, decimal_places=2)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    @transaction.atomic()
    def make_cancel(self):
        if self.order.status == OrderStatus.CREATED:
            self.order.make_cancel()
            self.save()
            return True
        return False

    @property
    def payment_url(self) -> str:
        # TODO add payment deposit
        return f'http://fake/{self.order.pk}'

    @property
    def transaction_url(self) -> str:
        url = self.order.currency.network.block_explorer_url
        return f'{url}/{self.order.transaction.transaction_hash}'

    @property
    def costumer(self) -> User:
        return self.order.user

    @property
    def status(self) -> OrderStatus:
        return self.order.status

    def get_status_display(self) -> str:
        return self.order.get_status_display()

    @property
    def create(self):
        return self.order.created

    @property
    def update(self):
        return self.order.updated

    @property
    def confirmed(self):
        return self.order.confirmed
