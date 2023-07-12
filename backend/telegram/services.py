import telebot

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


def update_messages(obj: models.Model, text: str, bot: telebot.TeleBot):
    obj = MessageIDS.objects.filter(
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
    ).first()
    if not obj:
        return None

    for message_id in obj.get_ids():
        bot.edit_message_text(
            text=text,
            message_id=message_id,
        )


@transaction.atomic()
def del_message(obj: models.Model):
    qs = MessageIDS.objects.filter(
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
    )

    if qs.exists():
        qs.delete()
