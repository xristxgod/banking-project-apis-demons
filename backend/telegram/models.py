from django.db import models, transaction
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class MessageIDS(models.Model):
    ids = models.JSONField(_('Message ids'), default={'ids': []})
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Message ids')
        verbose_name_plural = _('Messages ids')

    @transaction.atomic()
    def add(self, message_id: int):
        if message_id not in self.ids['ids']:
            self.ids['ids'].append(message_id)
            self.save()

    def get_ids(self) -> list:
        return self.ids['ids']
