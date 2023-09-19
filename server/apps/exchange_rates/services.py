from config.database import session_maker, extra_session_maker

from core.common.models import Model
from core.common.services import JSONModel, AbstractModelService

from apps.exchange_rates.dao import CryptoCurrencyDAO, FiatCurrencyDAO


class CurrencyServiceMixin:
    @classmethod
    async def simple_create(cls, model: JSONModel, **kwargs) -> Model:
        async with session_maker() as session:
            if not hasattr(model, 'id') or not await cls.dao.exists(filters=[cls.dao.model.id == model.id]):
                obj = await cls.dao.create(
                    obj=cls.dao.model(
                        **model.to_json(),
                    ),
                    session=session,
                    **kwargs,
                )
            async with extra_session_maker[cls.dao.extra_db]() as extra_session:
                if not await cls.dao.has_rate_table(obj=obj, session=extra_session):
                    await cls.dao.create_rate_model(
                        obj=obj,
                        session=extra_session,
                        **kwargs,
                    )
            return obj

    @classmethod
    async def create(cls, models: list[JSONModel], **kwargs):
        for model in models:
            await cls.simple_create(model=model)


class CryptoCurrencyService(CurrencyServiceMixin, AbstractModelService):
    dao = CryptoCurrencyDAO


class FiatCurrencyService(CurrencyServiceMixin, AbstractModelService):
    dao = FiatCurrencyDAO
