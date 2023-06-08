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


@pytest.fixture()
def mock_elastic(mocker):
    from unittest.mock import AsyncMock
    async_mock = AsyncMock()
    mocker.patch(
        'src.services.elastic.elastic._make_request',
        side_effect=async_mock
    )
    return async_mock
