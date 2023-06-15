import decimal
import enum

from tortoise import models, fields


class User(models.Model):
    id = fields.BinaryField(pk=True)
    username = fields.CharField(max_length=255, null=True, default=None)

    balance = fields.DecimalField(max_digits=25, decimal_places=25, default=0)

    created = fields.DatetimeField(auto_now=True)
    updated = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'telegram_user'

    @property
    def correct_balance(self) -> str:
        return f'{self.balance} $'

    @property
    def chat_id(self) -> int:
        return self.id

    chatId = chat_id        # alias


class Order(models.Model):
    class Status(enum.IntEnum):
        CREATED = 0
        SENT = 1
        DONE = 2

    id = fields.BigIntField(pk=True)
    amount = fields.DecimalField(max_digits=25, decimal_places=25, default=0)
    status = fields.IntEnumField(enum_type=Status, default=Status.CREATED)

    user = fields.ForeignKeyField('models.User', related_name='orders', on_delete=fields.RESTRICT)
    currency = fields.ForeignKeyField('models.Currency', related_name='orders', on_delete=fields.RESTRICT)

    created = fields.DatetimeField(auto_now=True)
    updated = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'telegram_order'

    @property
    def real_amount(self) -> decimal.Decimal:
        return self.convert.amount


class OrderTransaction(models.Model):
    id = fields.CharField(max_length=255, pk=True)
    timestamp = fields.BigIntField()
    order = fields.OneToOneField('models.Order', related_name='transaction', on_delete=fields.RESTRICT)
    commission = fields.DecimalField(max_digits=25, decimal_places=25, default=0)

    class Meta:
        table = 'telegram_transaction'


class ConvertOrderAmount:
    order = fields.OneToOneField('models.Order', related_name='convert', on_delete=fields.RESTRICT)
    usd_course = fields.DecimalField(max_digits=25, decimal_places=2, default=0)
    amount = fields.DecimalField(max_digits=25, decimal_places=2, default=0)
    commission = fields.DecimalField(max_digits=25, decimal_places=2, default=0)        # Service commission

    class Meta:
        table = 'telegram_convert_order_amount'
