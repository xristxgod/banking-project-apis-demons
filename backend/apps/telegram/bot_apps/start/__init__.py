from aiogram import Dispatcher

from . import handlers


def init_handlers(dp: Dispatcher):
    # Start
    dp.register_message_handler(
        handlers.start,
        commands=['start'],
    )
