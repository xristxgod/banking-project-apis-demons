import os

import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client():
    from httpx import AsyncClient
    from main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    from tortoise import Tortoise
    import settings

    await Tortoise.init(config=settings.DATABASE_CONFIG, _create_db=True)
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()
    await Tortoise._drop_databases()

    if settings.DATABASE_PATH.is_file():
        # Delete test.db
        settings.DATABASE_PATH.unlink()
