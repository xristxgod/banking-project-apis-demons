import uuid

import pytest

from apps.transaction.schemas import TransactionType
from apps.transaction.storage import TransactionStorage


class FakeTransaction:
    def __init__(self, id: str, is_expired: bool = True):
        self._id = id
        self._is_expired = is_expired

    @property
    def id(self):
        return self._id

    @property
    def is_expired(self):
        return self._is_expired


class FakeCreateTransactionSchema:
    def __init__(self, type: TransactionType):
        self.type = type

    @property
    def transaction_type(self):
        return self.type


@pytest.mark.asyncio
@pytest.mark.parametrize('type, obj_name', [
    (
            TransactionType.TRANSFER_NATIVE,
            'NativeTransfer',
    ),
    (
            TransactionType.TRANSFER,
            'Transfer',
    ),
    (
            TransactionType.APPROVE,
            'Approve',
    ),
    (
            TransactionType.TRANSFER_FROM,
            'TransferFrom',
    ),
])
async def test_transaction_storage(type, obj_name, mocker):
    storage = TransactionStorage()
    fake_id = str(uuid.uuid4())

    mocker.patch(
        f'apps.transaction.services.{obj_name}.create',
        return_value=FakeTransaction(fake_id)
    )

    body = FakeCreateTransactionSchema(type=type)

    obj = await storage.create(body, save=False)
    assert isinstance(obj, FakeTransaction)

    try:
        storage.get(fake_id)
        raise AssertionError()
    except storage.TransactionNotFound:
        pass

    obj = await storage.create(body)

    assert storage.get(fake_id, False) == obj
    assert storage.get(fake_id) is not None

    try:
        storage.get(fake_id)
        raise AssertionError()
    except storage.TransactionNotFound:
        pass

    fake_id2 = str(uuid.uuid4())
    fake_id3 = str(uuid.uuid4())

    storage.transactions[fake_id] = FakeTransaction(fake_id, False)
    storage.transactions[fake_id2] = FakeTransaction(fake_id, True)
    storage.transactions[fake_id3] = FakeTransaction(fake_id, False)

    assert len(storage.transactions) == 3

    await storage.clear_buffer()

    assert len(storage.transactions) == 1

    assert storage.transactions.get(fake_id2) is not None
