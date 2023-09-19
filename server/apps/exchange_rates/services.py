from config.database import session_maker, extra_session_maker
from core.common.services import JSONModel, AbstractModelService

from apps.exchange_rates.dao import CryptoCurrencyDAO


class CryptoCurrencyService(AbstractModelService):
    dao = CryptoCurrencyDAO

    @classmethod
    async def simple_create(cls, model: JSONModel, **kwargs):
        async with session_maker() as session:
            if not await cls.dao.exists(filters=[cls.dao.model.id == model.id]):
                obj = await cls.dao.create(
                    obj=cls.dao.model(
                        **model.to_json(),
                    ),
                    session=session,
                )
            async with extra_session_maker[cls.dao.extra_db]() as extra_session:
                if not await cls.dao.has_rate_table(obj=obj, session=extra_session):
                    await cls.dao.create_rate_model(
                        obj=obj,
                        session=extra_session,
                    )

    @classmethod
    async def create(cls, models: list[JSONModel], **kwargs):
        for model in models:
            await cls.simple_create(model=model)
