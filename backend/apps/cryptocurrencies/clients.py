import decimal
from urllib.parse import urljoin

import requests
from django.conf import settings

from src.meta import Singleton
from src.caches.ram import cached
from apps.cryptocurrencies.models import Currency


class CryptoExchangeAPIClient(metaclass=Singleton):
    headers = {
        'X-CoinAPI-Key': settings.CRYPTO_EXCHANGE_API_KEY
    }

    def __init__(self):
        self.endpoint_uri = settings.CRYPTO_EXCHANGE_URI
        self.session = requests.session()

    def _make_request(self, path: str) -> dict:
        url = urljoin(self.endpoint_uri, path)
        response = self.session.get(url, headers={})
        response.raise_for_status()
        return response.json()

    @cached(60 * 10)
    def get_currency_to_usdt_rate(self, currency: Currency) -> dict:
        response = self._make_request(
            path=f'/exchangerate/{currency.exchange_id}/USD',
        )

        return {
            'price': decimal.Decimal(round(response['rate'], 2)),
            'last_updated_at': response['time'],
        }


crypto_exchange_client = CryptoExchangeAPIClient()
