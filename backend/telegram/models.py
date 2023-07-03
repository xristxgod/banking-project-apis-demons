from django.db import models, transaction
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class TelegramMessageIDStorage(models.Model):
    ids = models.JSONField(default=[])
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Telegram message id storage')
        verbose_name_plural = _('Telegram message id storages')
