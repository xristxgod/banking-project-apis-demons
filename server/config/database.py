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
