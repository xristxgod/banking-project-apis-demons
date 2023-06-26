from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.BigIntegerField(_('Chat id'), primary_key=True)
    password = models.CharField(_('Password'), max_length=128, blank=True, null=True, default=None)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    @property
    def telegram_username(self) -> str:
        return f'@{self.username}'
