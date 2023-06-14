from django.db import models
from django.utils.translation import gettext as _


class AbstractCurrency(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    symbol = models.CharField(_('Symbol'), max_length=255)
    decimal_place = models.CharField(_('Decimal place'))

    @property
    def decimals(self) -> str:
        return 10 ** self.decimal_place

    class Meta:
        abstract = True


class Network(AbstractCurrency):
    url = models.URLField(_('Node url'))


class StableCoin(AbstractCurrency):
    address = models.CharField(_('Contract address'), max_length=255)
    network = models.ForeignKey(Network, verbose_name=_('Network'), on_delete=models.CASCADE)

    testnet = models.BooleanField(_('Testnet'), default=False)

    @property
    def is_testnet(self) -> bool:
        return self.testnet
