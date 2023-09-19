from typing import Any

import redis
import aioredis


class RedisConnector:
    def __init__(self, uri: str):
        self.async_connect = aioredis.from_url(uri)
        self.sync_connect = redis.from_url(uri)

    def sync_get(self, key: Any) -> Any:
        return self.sync_connect.get(key)

    async def async_get(self, key: Any) -> Any:
        return self.async_connect.get(key)

    def sync_set(self, key: Any, value: Any) -> Any:
        self.sync_connect.set(key, value)

    async def async_set(self, key: Any, value: Any) -> Any:
        await self.async_connect.set(key, value)

    def sync_delete(self, key: Any):
        self.sync_connect.delete(key)

    async def async_delete(self, key: Any):
        await self.async_connect.delete(key)
