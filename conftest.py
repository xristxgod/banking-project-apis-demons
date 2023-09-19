from typing import Optional

import pytest
from faker import Faker

from config.database import create_database, drop_database


"""

--- Global fixtures ---

"""


@pytest.fixture(scope='session')
def faker() -> Faker:
    return Faker()


"""

--- Asyncio ---

"""


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope='session')
def event_loop():
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


"""

--- FastApi ---

"""


@pytest.fixture(scope='session')
async def client():
    from httpx import AsyncClient
    from main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


"""

--- Database ---

"""


@pytest.fixture(scope='session', autouse=True)
async def init_default_database():
    from config.database import Base, engine

    await create_database(db_name='tests-merchant-db')
    await create_database(db_name='tests-exchange-rate-db')

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await drop_database(db_name='tests-exchange-rate-db')
    await drop_database(db_name='tests-merchant-db')


@pytest.fixture(scope='session')
async def dbsession():
    from config.database import session_maker

    async with session_maker() as session:
        yield session


@pytest.fixture(scope='session')
def get_dbsession():
    async def dbsession(db_name: Optional[str] = None):
        from config.database import session_maker, extra_session_maker
        async with extra_session_maker.get(db_name, session_maker)() as session:
            yield session

    return dbsession
