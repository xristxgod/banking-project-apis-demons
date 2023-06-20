from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.BigIntegerField(_('Chat id'), primary_key=True)

    balance = models.DecimalField(_('Balance'), max_digits=25, decimal_places=25, default=0)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
