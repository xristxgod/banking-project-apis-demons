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

    @property
    def txid(self):
        return self.id

    def sign(self, priv_key):
        assert isinstance(priv_key, PrivateKey)
        self._private_key = priv_key
        return self

    @property
    def is_expired(self):
        return self._is_expired

    async def update(self):
        self._is_expired = True

    async def broadcast(self):
        return FakeTransactionRet()


class FakeTransactionRet(AsyncTransactionRet):
    def __init__(self):
        pass

    async def wait(self):
        pass

