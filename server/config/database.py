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

    def decorator(func):
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
