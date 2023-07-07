from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType

from telegram.models import MessageIDS


@transaction.atomic()
def save_message(message_id: int, obj: models.Model):
    qs = MessageIDS.objects.filter(
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
    )
    if qs.exists():
        obj = qs.first()
    else:
        obj = MessageIDS.objects.create(
            content_object=obj,
        )
    obj.add(message_id)
