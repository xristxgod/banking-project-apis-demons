import typing

from . import start
from . import orders
from .base.handlers import AbstractHandler

__all__ = (
    'APPS_HANDLERS',
)

APPS_HANDLERS: list[typing.Type[AbstractHandler]] = [
    *start.HANDLERS,
    *orders.HANDLERS,
]
