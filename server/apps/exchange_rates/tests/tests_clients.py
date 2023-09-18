import time
import decimal

import pytest
from unittest import mock

import settings
from apps.exchange_rates.clients import CoinGeckoClient, ExchangeRateClient


def get_mock_make_request(mth: str, return_value: dict, prm: dict = None):
    async def mock_make_request(method: str, params: dict = None):
        assert method == mth
        assert params == prm
        return return_value
    return mock_make_request


@pytest.mark.anyio
async def test_coin_gecko_client_get_price(mocker):
    currencies = ['btc', 'eth', 'tron']

    return_value = {
        'btc': {'usd': 54000, 'last_updated_at': time.time_ns()},
        'eth': {'usd': 2451.24, 'last_updated_at': time.time_ns()},
        'tron': {'usd': 0.0012, 'last_updated_at': time.time_ns()},
    }

    mocker.patch(
        'apps.exchange_rates.clients.BaseClient.make_request',
        new=get_mock_make_request(
            mth='/api/v3/simple/price/',
            prm={
                'ids': 'btc,eth,tron',
                'vs_currencies': 'usd',
                'include_last_updated_at': 'true',
            },
            return_value=return_value
        )
    )

    result = await CoinGeckoClient.get_prices(currencies=currencies)
    assert result == {
        'btc': {
            'value': decimal.Decimal(repr(return_value['btc']['usd'])),
            'timestamp': return_value['btc']['last_updated_at'],
        },
        'eth': {
            'value': decimal.Decimal(repr(return_value['eth']['usd'])),
            'timestamp': return_value['eth']['last_updated_at'],
        },
        'tron': {
            'value': decimal.Decimal(repr(return_value['tron']['usd'])),
            'timestamp': return_value['tron']['last_updated_at'],
        },
    }


@pytest.mark.anyio
@mock.patch('settings.EXCHANGERATE_API_KEY', 'test-api-key')
async def test_exchange_rate_get_price(mocker):
    currencies = ['RUB', 'EUR', 'ARS']
    return_value = {
        'conversion_rates': {
            'RUB': 95.51,
            'ARS': 21.2,
        },
        'time_last_update_unix': time.time_ns(),
    }

    mocker.patch(
        'apps.exchange_rates.clients.BaseClient.make_request',
        new=get_mock_make_request(
            mth=f'/v6/{settings.EXCHANGERATE_API_KEY}/latest/USD',
            return_value=return_value.copy(),
        )
    )

    result = await ExchangeRateClient.get_prices(currencies=currencies)
    assert result == {
        'RUB': {
            'value': decimal.Decimal(repr(return_value['conversion_rates']['RUB'])),
            'timestamp': return_value['time_last_update_unix'],
        },
        'ARS': {
            'value': decimal.Decimal(repr(return_value['conversion_rates']['ARS'])),
            'timestamp': return_value['time_last_update_unix'],
        }
    }
