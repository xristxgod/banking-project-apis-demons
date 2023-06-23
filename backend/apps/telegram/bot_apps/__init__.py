import typing

from . import start
from . import orders
from .base.handlers import AbstractHandler

from . import middlewares
from . import filters

__all__ = (
    'middlewares',
    'filters',
    'APPS_HANDLERS',
)

APPS_HANDLERS: list[typing.Type[AbstractHandler]] = [
    *start.HANDLERS,
    *orders.HANDLERS,
]
