from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

import settings

Base = declarative_base()

async_engine = create_async_engine(settings.DATABASE_URL.replace('postgresql', 'postgresql+asyncpg'))
async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

engine = create_engine(settings.DATABASE_URL)
session_maker = sessionmaker(autoflush=False, bind=engine)
