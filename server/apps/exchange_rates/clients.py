import abc
import decimal
from typing import Optional

import aiohttp

import settings


class BaseClient(metaclass=abc.ABC):
    url: str
    headers: dict = {}

    @classmethod
    async def make_request(cls, method: str, params: Optional[dict] = None) -> dict:
        async with aiohttp.ClientSession(base_url=cls.url, headers=cls.headers) as session:
            async with session.get(method, params=params or {}) as response:
                response.raise_for_status()
                response = await response.json()
        return response

    @abc.abstractclassmethod
    async def get_prices(cls, currency: list[str]) -> dict: ...


class CoinGeckoClient(BaseClient):
    """Crypto exchange"""
    url = 'https://api.coingecko.com/'

    @classmethod
    async def get_prices(cls, coins: list[str]) -> dict:
        response = await cls.make_request(
            method='/api/v3/simple/price/',
            params={
                'ids': ','.join(coins),
                'vs_currencies': 'usd',
                'include_last_updated_at': 'true',
            }
        )
        return {
            coin: {
                'value': decimal.Decimal(repr(info['usd'])),
                'time': info['last_updated_at'],
            }
            for coin, info in response.items()
        }


class ExchangeRateClient(BaseClient):
    """Fiat exchange"""
    uri = 'https://v6.exchangerate-api.com/'

    @classmethod
    async def get_prices(cls, coins: list[str]):
        response = await cls.make_request(
            method=f'/v6/{settings.EXCHANGERATE_API_KEY}/latest/USD',
        )
        result = {}
        for coin in coins:
            price = response['conversion_rates'].get(coin.upper(), 0)
            result.update({
                coin: {
                    'value': decimal.Decimal(repr(price)),
                    'time': response['time_last_update_unix'],
                }
            })
        return result
