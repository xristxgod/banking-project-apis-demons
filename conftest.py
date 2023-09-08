import pytest


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


@pytest.fixture(scope='session')
async def client():
    from httpx import AsyncClient
    from main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope='session')
async def db_session():
    from config.database import session_maker

    async with session_maker() as session:
        yield session
