import pytest


@pytest.mark.django_db
def test_save_message():
    from telegram.models import MessageIDS
    from telegram.services import save_message
    from apps.orders.tests.factories import PaymentFactory
    from apps.orders.models import Payment
    from django.contrib.contenttypes.models import ContentType

    payment = PaymentFactory(is_created=True)
    message_ids = [1, 2, 3, 5]

    for message_id in message_ids:
        save_message(message_id=message_id, obj=payment)

    storage = MessageIDS.objects.get(
        content_type=ContentType.objects.get_for_model(payment),
        object_id=payment.pk,
    )

    assert storage.get_ids() == message_ids
