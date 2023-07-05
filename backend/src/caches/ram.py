import inspect
import hashlib
import functools
import operator
from datetime import datetime, timedelta

from django.db import models
from django.utils.encoding import smart_str

from src.meta import Singleton

__all__ = (
    'cached',
)


class Cached(metaclass=Singleton):

    @classmethod
    def _vary_on(cls, function, args, kwargs):
        args_names = inspect.getfullargspec(function)[0]
        if len(args_names) > 0 and args_names[0] in ('self', 'cls'):
            args = args[1:]
            args_names = args_names[1:]

        params = kwargs.copy()
        for q, arg_value in enumerate(args):
            try:
                arg_name = args_names[q]
            except IndexError:
                arg_name = 'arg_{}'.format(q)
            if arg_name not in params:
                params[arg_name] = arg_value

        result = []
        for k, v in sorted(params.items(), key=lambda x: x[0]):
            result.extend([k, v.pk if isinstance(v, models.Model) else v])
        return result

    def __init__(self):
        self._storage = {}

    def get_slot_name(self, function, args, kwargs) -> str:
        params = self._vary_on(function, args, kwargs)
        return u':'.join([
            f'cache-{function.__module__}.{function.__name__}',
            hashlib.sha256(functools.reduce(
                operator.add,
                map(smart_str, params)
            ).encode('utf-8')).hexdigest() if params else ''
        ])

    def cached(self, ttl: float | int):
        def decorator(function):
            def wrapper(*args, **kwargs):
                key = self.get_slot_name(function, args, kwargs)
                result, t = self._storage.get(key, (None, datetime.min))

                if datetime.now() > t + timedelta(seconds=ttl):
                    self._storage.pop(key, None)
                    result = None

                if result is None:
                    result = function(*args, **kwargs)
                    self._storage[key] = (result, datetime.now())

                return result

            return wrapper

        return decorator

    def __call__(self, ttl: int):
        return self.cached(ttl=ttl)


cached = Cached()
