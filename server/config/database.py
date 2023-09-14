import functools
from typing import Callable, Optional

from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine, create_async_engine

import settings

Base = declarative_base()
metadata = Base.metadata

engine: AsyncEngine = create_async_engine(settings.DATABASES['default'])
session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
extra_engines = {
    'exchange-rate': create_async_engine(settings.DATABASES['exchange-rate']),
}
extra_session_maker = {
    'exchange-rate': async_sessionmaker(extra_engines['exchange-rate'], class_=AsyncSession, expire_on_commit=False),
}


def db_query_handler(db: str = 'default'):
    _session_maker = session_maker if db == 'default' else extra_session_maker[db]

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            if kwargs.get('session'):
                return await func(*args, **kwargs)
            async with _session_maker() as session:
                try:
                    kwargs['session'] = session
                    return await func(*args, **kwargs)
                except Exception as err:
                    await session.rollback()
                    raise err
        return wrapper

    return decorator


def dynamic_db_query_handler(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if kwargs.get('session'):
            return await func(*args, **kwargs)

        if args and hasattr(args[0], 'db'):
            db = getattr(args[0], 'db')
        elif kwargs.get('cls') and hasattr(kwargs['cls'], 'db'):
            db = getattr(kwargs['cls'], 'db')
        elif kwargs.get('self') and hasattr(kwargs['self'], 'db'):
            db = getattr(kwargs['cls'], 'db')
        else:
            db = 'default'

        _session_maker = session_maker if db == 'default' else extra_session_maker[db]
        async with _session_maker() as session:
            try:
                kwargs.update({
                    'session': session,
                })
                return await func(*args, **kwargs)
            except Exception as err:
                await session.rollback()
                raise err

    return wrapper


async def get_tables(e: Optional[AsyncEngine] = None):
    from sqlalchemy import inspect
    e = e or engine
    async with e.connect() as connection:
        tables = await connection.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
    return tables


async def has_table(table_name: str, e: Optional[AsyncEngine] = None):
    e = e or engine
    tables = await get_tables(e=e)
    return table_name in tables
