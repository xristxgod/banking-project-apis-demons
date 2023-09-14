import json
from typing import Any
from datetime import datetime, timedelta

import redis
import aioredis

import settings
from core.common.caches.ram import Cache


class BaseCache(Cache):
    uri: str

    __slots__ = (
        '_connection',
        '_sync_connection'
    )

    def setup(self):
        self._connection = aioredis.from_url(self.uri)
        self._sync_connection = redis.from_url(self.uri)

    def _sync_get_actual_result(self, key: str, ttl: int | float) -> tuple:
        result, t = (None, datetime.min)
        if value := self._sync_connection.get(key):
            result, t = json.loads(value)

        if datetime.now() > t + timedelta(seconds=ttl):
            self._sync_connection.delete(key)
            result = None
        return result, t

    async def _async_get_actual_result(self, key: str, ttl: int | float) -> tuple:
        result, t = (None, datetime.min)
        if value := await self._connection.get(key):
            result, t = json.loads(value)

        if datetime.now() > t + timedelta(seconds=ttl):
            await self._connection.delete(key)
            result = None
        return result, t

    def _sync_set_actual_result(self, key: str, result: Any):
        self._sync_connection.set(key, json.dumps(result, default=str))

    async def _async_set_actual_result(self, key: str, result: Any):
        await self._connection.set(key, json.dumps(result, default=str))


class DefaultCached(BaseCache):
    uri = settings.CACHED_BACKEND_URL


cached = DefaultCached()
