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
