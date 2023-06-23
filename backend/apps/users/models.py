from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    password = models.CharField(_('Password'), max_length=128, blank=True, null=True, default=None)

    chat_id = models.BigIntegerField(_('Chat id'), blank=True, null=True, default=None, unique=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    @property
    def telegram_username(self) -> str:
        return f'@{self.username}'
