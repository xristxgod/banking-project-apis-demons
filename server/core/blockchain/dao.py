from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.common.dao import BaseDAO
from core.common.caches import ram_cached
from core.blockchain import models


class NetworkDAO(BaseDAO):
    model = models.Network

    @classmethod
    @ram_cached(60)
    async def get_current_networks(cls, *, session: Optional[AsyncSession] = None) -> list[model]:
        from sqlalchemy.sql.expression import true
        return await cls.filter(
            filters=[cls.model.is_active == true()],
            session=session,
        )


class StableCoinDAO(BaseDAO):
    model = models.StableCoin


class OrderProviderDAO(BaseDAO):
    model = models.OrderProvider
