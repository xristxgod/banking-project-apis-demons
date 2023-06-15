from __future__ import annotations

import enum

from tortoise import models, fields, transactions


class Language(models.Model):
    name = fields.CharField(max_length=50)
    short_name = fields.CharField(max_length=3)

    class Meta:
        table = 'telegram_language'

    @property
    def tag(self) -> str:
        return self.short_name.lower()

    @classmethod
    async def default(cls) -> Language:
        # Default: ENG
        return await cls.get(id=1)


class User(models.Model):
    id = fields.BinaryField(pk=True)
    username = fields.CharField(max_length=255, null=True, default=None)

    balance = fields.DecimalField(max_digits=25, decimal_places=25, default=0)

    language = fields.ForeignKeyField('models.Language', related_name='users', on_delete=fields.RESTRICT)

    created = fields.DatetimeField(auto_now=True)
    updated = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'telegram_user'

    @transactions.atomic()
    def change_language(self, language: Language):
        self.language = language
        await self.save()

    @property
    def correct_balance(self) -> str:
        return f'{self.balance} $'

    @property
    def chat_id(self) -> int:
        return self.id

    chatId = chat_id        # alias:


class TelegramAppsType(enum.IntEnum):
    START = 0


class TelegramText(models.Model):
    id = fields.CharField(max_length=50, pk=True)
    apps_type = fields.IntEnumField(enum_type=TelegramAppsType)

    text_ru = fields.CharField(max_length=500, default='пусто')
    text_eng = fields.CharField(max_length=500, default='empty')
