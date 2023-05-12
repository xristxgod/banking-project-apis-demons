import decimal

import pytest

from core.crypto import node
from core.crypto.utils import from_sun
from .factories import create_fake_contract, fake_address


FAKE_SIGNATURE = (
    '00000000000000000000000000000000000000000000000000000000000000000'
    '00000000000000000000000000000000000000000000000000000000000000000'
)


@pytest.mark.asyncio
class TestResource:

    @pytest.fixture(scope="session", autouse=True)
    async def setup(self):
        await create_fake_contract(symbol='USDT')
        await create_fake_contract(symbol='USDC')

    @pytest.mark.parametrize('raw_data, is_active, result', [
        (
                {
                    'contract': [{
                        'type': 'TransferContract',
                        'parameter': {
                            'value': {
                                'to_address': fake_address(True),
                            }
                        }
                    }]
                },
                False,
                {
                    'fee': decimal.Decimal(1.1),
                    'bandwidth': 100,
                    'energy': 0,
                }

        ),
        (
                {
                    'contract': [{
                        'type': 'TransferContract',
                        'parameter': {
                            'value': {
                                'to_address': fake_address(True),
                            }
                        }
                    }]
                },
                True,
                None,
        ),
        (
                {
                    'contract': [{
                        'type': 'Fake',
                    }]
                },
                False,
                None,
        )
    ])
    async def test_pre_calculate(self, raw_data, is_active, result, mocker):
        mocker.patch(
            'core.crypto.node.Node.is_active_address',
            return_value=is_active,
        )

        response = await node.calculator._pre_calculate(raw_data)

        assert response == result

    @pytest.mark.parametrize('params, bandwidth, energy', [
        (
                {
                    'raw_data': {},
                },
                245,
                0,
        ),
        (
                {
                    'raw_data': {},
                },
                245,
                0,
        ),
        (
                {
                    'raw_data': {},
                    'owner_address': fake_address(),
                    'parameter': [],
                    'currency': 'USDT',
                    'function_selector': True,
                },
                365,
                12_000,
        ),
        (
                {
                    'raw_data': {},
                    'owner_address': fake_address(),
                    'parameter': [],
                    'currency': 'USDC',
                    'function_selector': True,
                },
                365,
                12_000,
        ),
    ])
    async def test_calculate(self, params, bandwidth, energy, mocker):
        mocker.patch(
            'core.crypto.calculator.Resource.get_transaction_bandwidth_cost',
            return_value=bandwidth,
        )
        mocker.patch(
            'core.crypto.calculator.Resource.get_transaction_energy_cost',
            return_value=energy,
        )
        mocker.patch(
            'core.crypto.calculator.FeeCalculator._pre_calculate',
            return_value=None,
        )

        response = await node.calculator.calculate(
            **params
        )

        assert isinstance(response, dict)
        assert response['fee'] == from_sun(energy * 400) + from_sun(bandwidth * 1000)
        assert response['energy'] == energy
        assert response['bandwidth'] == bandwidth
