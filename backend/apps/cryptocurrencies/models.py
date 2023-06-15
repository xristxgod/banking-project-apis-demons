from tortoise import models, fields


class Network(models.Model):
    name = fields.CharField(max_length=255, pk=True)

    class Meta:
        table = 'cryptocurrencies_network'


class Currency(models.Model):
    name = fields.CharField(max_length=255, pk=True)
    symbol = fields.CharField(max_length=255)
    network = fields.ForeignKeyField('models.Network', related_name='currencies', on_delete=fields.RESTRICT)
    address = fields.CharField(max_length=255, null=True, default=None)
    decimal_place = fields.IntField(null=True, default=6)

    @property
    def is_stable_coin(self) -> bool:
        return self.address is not None

    class Meta:
        table = 'cryptocurrencies_currency'
