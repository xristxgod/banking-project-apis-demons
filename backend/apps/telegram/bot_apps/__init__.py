from aiogram import Dispatcher

from . import start


def init_all_handlers(dp: Dispatcher):
    start.init_handlers(dp)
