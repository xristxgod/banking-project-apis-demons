import decimal

import pytest
from unittest.mock import AsyncMock

from tests.factories import fake_transaction, fake_stable_coin

from core.schemas import TransactionType, Commission
from core.transaction import Transaction


@pytest.mark.asyncio
class TestTransaction:
    obj = Transaction

    @pytest.mark.parametrize('typ, is_active', [
        (TransactionType.TRANSFER, False),
        (TransactionType.TRANSFER, True),
    ])
    async def test_native_commission(self, typ, is_active, mocker):
        from tronpy.async_tron import AsyncTron
        mocker.patch(
            'core.node.Node.is_active_address',
            side_effect=AsyncMock(),
            return_value=True
        )

        transaction = fake_transaction(typ=typ, is_signed=True)

        result = await self.obj.commission(
            raw_data=transaction['raw_data'],
            signature=transaction['signature'][0],
            client=AsyncTron(),
        )

        assert isinstance(result, Commission)

    @pytest.mark.parametrize('typ, energy_used', [
        (TransactionType.TRANSFER, 10_000),
        (TransactionType.APPROVE, 10_000),
        (TransactionType.TRANSFER_FROM, 15_000),
    ])
    async def test_stable_coin_commission(self, typ, energy_used):
        from tronpy.async_tron import AsyncTron
        from core.utils import from_sun

        class FakeClient(AsyncTron):
            def __init__(self):
                pass

            async def trigger_constant_contract(self, **kwargs):
                return {'energy_used': energy_used}

        stable_coin = fake_stable_coin()
        transaction = fake_transaction(typ=typ, is_signed=True, contract_address=stable_coin.address,
                                       decimal_place=stable_coin.decimal_place)

        result = await self.obj.commission(
            raw_data=transaction['raw_data'],
            signature=transaction['signature'][0],
            client=FakeClient(),
        )

        assert isinstance(result, Commission)
        assert from_sun(result.bandwidth * 400 + energy_used * 1000) == result.amount

    @pytest.mark.parametrize('typ, commission', [
        (TransactionType.TRANSFER, Commission(amount=decimal.Decimal(0), bandwidth=256, energy=0)),
        (TransactionType.FREEZE, Commission(amount=decimal.Decimal(0), bandwidth=256, energy=0)),
        (TransactionType.UNFREEZE, Commission(amount=decimal.Decimal(0), bandwidth=256, energy=0)),
    ])
    async def test_native_make_response(self, typ, commission, mocker):
        pass