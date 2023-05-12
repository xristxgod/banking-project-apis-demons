from tronpy.keys import PrivateKey
from tronpy.async_tron import AsyncTransaction, AsyncTransactionRet, AsyncTransactionBuilder

from core.crypto.tests.factories import fake


def fake_amount():
    return fake.unique.pydecimal(left_digits=4, right_digits=6, positive=True)


class FakeTransactionBuilder(AsyncTransactionBuilder):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self._fee_limit = None
        self._is_building = False

    def fee_limit(self, value):
        self._fee_limit = value
        return self

    def assert_fee_limit(self, value):
        assert self._fee_limit == value

    async def build(self, **kwargs):
        self._is_building = True
        return FakeTransaction(id=self.id)

    def assert_use_builder(self):
        assert self._is_building


class FakeTransaction(AsyncTransaction):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self._raw_data = {}
        self._private_key = None
        self._is_expired = True
        self._signed = False
        self._raw_transaction = kwargs.get('raw_transaction')
        self._transaction_info = kwargs.get('transaction_info')

    @property
    def txid(self):
        return self.id

    def sign(self, priv_key):
        assert isinstance(priv_key, PrivateKey)
        self._private_key = priv_key
        self._signed = True
        return self

    def assert_sign(self, private_key):
        assert self._private_key == private_key
        assert self._signed

    @property
    def is_expired(self):
        return self._is_expired

    @is_expired.setter
    def is_expired(self, value):
        self._is_expired = value

    async def update(self):
        self._is_expired = True

    async def broadcast(self):
        return FakeTransactionRet(self._raw_transaction, self._transaction_info)


class FakeTransactionRet(dict):
    def __init__(self, iterable, info):
        super().__init__(iterable)

        self._info = info

    async def wait(self):
        return self._info

