import asyncio
import hashlib
import inspect
import operator
import functools
from typing import Any
from datetime import datetime, timedelta

from config.database import Base
from core.common.meta import Singleton


class Cached(metaclass=Singleton):
    @classmethod
    def _vary_on(cls, function: object, args, kwargs):
        args_names = inspect.getfullargspec(function)[0]
        if len(args_names) > 0 and args_names[0] in ('self', 'cls'):
            args = args[1:]
            args_names = args_names[1:]

        params = kwargs.copy()
        for q, arg_value in enumerate(args):
            try:
                arg_name = args_names[q]
            except IndexError:
                arg_name = f'arg_{q}'

            if arg_name not in params:
                params[arg_name] = arg_value

        result = []
        for key, value in sorted(params.items(), key=lambda x: x[0]):
            result.extend([key, value.id if isinstance(value, Base) else value])
        return result

    def __init__(self):
        self._storage: dict[str: tuple[Any, datetime]] = {}

    def get_slot_name(self, function: object, args, kwargs) -> str:
        params = self._vary_on(function, args, kwargs)
        return u':'.join([
            f'cache-{function.__module__}.{function.__name__}',
            hashlib.sha256(functools.reduce(
                operator.add,
                map(str, params),
            ).encode('utf-8')).hexdigest() if params else ''
        ])

    def _get_actual_result(self, key: str, ttl: int | float) -> tuple:
        result, t = self._storage.get(key, (None, datetime.min))
        if datetime.now() > t + timedelta(seconds=ttl):
            self._storage.pop(key, None)
            result = None
        return result, t

    def _set_actual_result(self, key: str, result: Any):
        self._storage[key] = (result, datetime.now())

    def cached(self, ttl: float | int):
        def decorator(function):
            @functools.wraps(function)
            def sync_wrapper(*args, **kwargs):
                key = self.get_slot_name(function, args, kwargs)
                result, t = self._get_actual_result(key=key, ttl=ttl)
                if result is None:
                    result = function(*args, **kwargs)
                    self._set_actual_result(key=key, result=result)
                return result

            @functools.wraps(function)
            async def async_wrapper(*args, **kwargs):
                key = self.get_slot_name(function, args, kwargs)
                result, t = self._get_actual_result(key=key, ttl=ttl)
                if result is None:
                    result = await function(*args, **kwargs)
                    self._set_actual_result(key=key, result=result)
                return result

            if asyncio.iscoroutinefunction(function):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def __call__(self, ttl: float | int = 60.00):
        return self.cached(ttl=ttl)


cached = Cached()
