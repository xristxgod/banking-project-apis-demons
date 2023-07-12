import pytest


@pytest.mark.django_db
def test_save_message():
    from django.contrib.contenttypes.models import ContentType

    from telegram.models import MessageIDS
    from telegram.services import save_message
    from apps.orders.tests.factories import PaymentFactory

    payment = PaymentFactory(is_created=True)
    message_ids = [1, 2, 3, 5]

    for message_id in message_ids:
        save_message(message_id=message_id, obj=payment)

    storage = MessageIDS.objects.get(
        content_type=ContentType.objects.get_for_model(payment),
        object_id=payment.pk,
    )

    assert storage.get_ids() == message_ids


def test_memory_storage():
    from telegram.bot_apps.base.storage import MemoryStorage, buffer

    class MockObject:
        pass

    mock_object = MockObject()
    key1 = 'test-key1'
    key2 = 'test-key2'

    storage_object_key = MemoryStorage(mock_object)

    storage_str_key1 = MemoryStorage(key1)
    storage_str_key1_duplicate = MemoryStorage(key1)

    storage_str_key2 = MemoryStorage(key2)

    assert len(buffer.keys()) == 3

    assert storage_object_key.key in buffer.keys()
    assert storage_str_key1.key in buffer.keys()
    assert storage_str_key1_duplicate.key in buffer.keys()
    assert storage_str_key2.key in buffer.keys()

    storage_object_key[1] = {
        'test': 1
    }

    assert storage_object_key.get(1) == {
        'step': {
            'callback': None,
            'set': False,
        },
        'data': {
            'test': 1
        },
    }
    assert storage_str_key1.get(1) is None

    storage_str_key1[1] = {
        'test': 1,
    }

    assert storage_str_key1.get(1) == {
        'step': {
            'callback': None,
            'set': False,
        },
        'data': {
            'test': 1
        },
    }
    assert storage_str_key1_duplicate.get(1) == {
        'step': {
            'callback': None,
            'set': False,
        },
        'data': {
            'test': 1
        },
    }
    assert storage_str_key2.get(1) is None

    storage_str_key1.update(1, test=2)

    assert storage_str_key1.get(1) == {
        'step': {
            'callback': None,
            'set': False,
        },
        'data': {
            'test': 2
        },
    }
