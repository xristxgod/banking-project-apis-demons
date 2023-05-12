import pytest

from .factories import create_fake_contract


@pytest.mark.asyncio
class TestResource:

    @pytest.fixture(scope="session", autouse=True)
    async def setup(self):
        await create_fake_contract(symbol='USDT')
        await create_fake_contract(symbol='USDC')

    async def test_get_transaction_bandwidth_cost(self, mocker):
        pass
