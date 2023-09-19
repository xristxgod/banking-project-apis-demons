from typing import Type, Optional

from sqlalchemy.schema import DropTable, CreateTable
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import metadata, db_query_handler, has_table
from core.common.dao import BaseDAO
from apps.exchange_rates.models import CryptoCurrency, FiatCurrency


class CurrencyDAOMixin:
    prefix: str = NotADirectoryError
    extra_db = 'exchange-rate'

    @classmethod
    def get_rate_table(cls, obj):
        import time
        import sqlalchemy as fields
        from sqlalchemy import Table, Column

        table = Table(
            f'{cls.prefix}_{obj.name.lower()}_rate', metadata,
            Column('timestamp', fields.TIMESTAMP, default=time.time_ns(), primary_key=True),
            Column('price', fields.Numeric(25, 3), default=0.0),
        )
        return table

    @classmethod
    @db_query_handler(db='exchange-rate')
    async def has_rate_table(cls, obj, *, session: Optional[AsyncSession] = None) -> bool:
        table_name = f'{cls.prefix}_{obj.name.lower()}_rate'
        return await has_table(table_name=table_name, e=session.bind)

    @classmethod
    @db_query_handler(db='exchange-rate')
    async def create_rate_model(cls, obj, *, session: Optional[AsyncSession] = None, **kwargs):
        table = cls.get_rate_table(obj=obj)

        sql = CreateTable(table)
        await session.execute(sql)
        if kwargs.get('auto_commit', False):
            await session.commit()

    @classmethod
    @db_query_handler(db='exchange-rate')
    async def drop_rate_model(cls, obj, *, session: Optional[AsyncSession] = None, **kwargs):
        table = cls.get_rate_table(obj=obj)
        sql = DropTable(table)
        await session.execute(sql)
        if kwargs.get('auto_commit', False):
            await session.commit()

    @classmethod
    async def get_rate_dao(cls, obj) -> Type[BaseDAO]:
        table = cls.get_rate_table(obj=obj)

        class RateDAO(BaseDAO):
            model = table
            db = cls.extra_db

        return RateDAO


class CryptoCurrencyDAO(CurrencyDAOMixin, BaseDAO):
    model = CryptoCurrency
    prefix = 'crypto'


class FiatCurrencyDAO(CurrencyDAOMixin, BaseDAO):
    model = FiatCurrency
    prefix = 'fiat'
