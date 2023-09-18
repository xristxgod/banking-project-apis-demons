import asyncio
from typing import Type

from config import celery_app
from core.common.dao import BaseDAO
from apps.exchange_rates.dao import CryptoCurrencyDAO, FiatCurrencyDAO
from apps.exchange_rates.clients import BaseClient, CoinGeckoClient, ExchangeRateClient


async def _parsing_rates(dao: Type[BaseDAO], client: Type[BaseClient], field_id: str):
    currencies = await dao.all()
    result = await client.get_prices(currency=[
        getattr(currency, field_id)
        for currency in currencies
    ])

    for currency in currencies:
        rate_obj = dao.get_rate_table(obj=currency)
        rate_dao = await dao.get_rate_dao(obj=currency)

        rate = result.get(getattr(currency, field_id), currency.default_price)
        await rate_dao.create(
            obj=rate_obj(
                timestamp=rate['timestamp'],
                price=rate['value'],
            ),
        )
    return True


@celery_app.task(acks_late=True)
def parsing_crypto_rates_task():
    return asyncio.run(_parsing_rates(
        dao=CryptoCurrencyDAO,
        client=CoinGeckoClient,
        field_id='coin_gecko_id',
    ))


@celery_app.task(acks_late=True)
def parsing_fiat_rates_task():
    return asyncio.run(_parsing_rates(
        dao=FiatCurrencyDAO,
        client=ExchangeRateClient,
        field_id='exchange_rate_id',
    ))
