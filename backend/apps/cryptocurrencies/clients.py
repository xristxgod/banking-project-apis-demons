import decimal
from urllib.parse import urljoin

import requests
from django.conf import settings

from src.meta import Singleton
from apps.cryptocurrencies.models import Currency


class CoinGeckoAPIClient(metaclass=Singleton):
    def __init__(self):
        self.endpoint_uri = settings.CRYPTO_EXCHANGE_URI
        self.session = requests.session()

    def _make_request(self, path: str) -> dict:
        url = urljoin(self.endpoint_uri, path)
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_currency_to_usdt_rate(self, currency: Currency) -> dict:
        response = self._make_request(
            path=f'/simple/price?ids={currency.coin_gecko_id}&vs_currencies=usd&include_last_updated_at=true'
        )

        coin = response[currency.coin_gecko_id]
        return {
            'price': decimal.Decimal(repr(coin['usd'])),
            'last_updated_at': coin['last_updated_at'],
        }


client = CoinGeckoAPIClient()
