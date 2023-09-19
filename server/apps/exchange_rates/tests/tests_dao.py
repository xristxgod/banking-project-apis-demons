import pytest

from core.common.services import JSONModel
from apps.exchange_rates.models import CryptoCurrency, FiatCurrency
from apps.exchange_rates.dao import CryptoCurrencyDAO, FiatCurrencyDAO
from apps.exchange_rates.services import CryptoCurrencyService, FiatCurrencyService


@pytest.mark.anyio
@pytest.mark.parametrize('model, obj, dao, service', [
    (JSONModel(name='Tron', coin_gecko_id='trx'), CryptoCurrency, CryptoCurrencyDAO, CryptoCurrencyService),
    (JSONModel(name='RUB', exchange_rate_id='rub'), FiatCurrency, FiatCurrencyDAO, FiatCurrencyService),
])
async def test_currency_dao(model, obj, dao, service):
    from config.database import extra_engines, has_table

    currency = await service.simple_create(model=model)

    assert currency.name == model.get('name')
    assert isinstance(currency, obj)

    extra_engine = extra_engines['exchange-rate']

    sub_table_name = dao.get_rate_table_name(obj=currency)
    assert await has_table(table_name=sub_table_name, e=extra_engine)

    await service.simple_delete(model=JSONModel(id=currency.id))

    assert not await dao.exists(filters=[obj.id == currency.id])
    assert not await has_table(sub_table_name, e=extra_engine)
