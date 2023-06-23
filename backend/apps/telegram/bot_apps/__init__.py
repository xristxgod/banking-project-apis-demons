import typing

from . import start
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
]
