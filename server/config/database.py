from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

import settings

Base = declarative_base()

engine = create_async_engine(settings.DATABASE_URL.replace('postgresql', 'postgresql+asyncpg'))
session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def db_query_handler(func):
    async def wrapper(*args, **kwargs):
        if kwargs.get('session'):
            return await func(*args, **kwargs)
        async with session_maker() as session:
            try:
                kwargs['session'] = session
                return await func(*args, **kwargs)
            except Exception as err:
                await session.rollback()
                raise err

    return wrapper
