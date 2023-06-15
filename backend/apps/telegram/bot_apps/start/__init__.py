from aiogram import Dispatcher

from . import handlers
from . import callbacks


def init_handlers(dp: Dispatcher):
    # Start
    dp.register_message_handler(
        handlers.start,
        commands=['start'],
    )
    # Registration
    dp.register_callback_query_handler(
        handlers.registration,
        callback=callbacks.registration_cb,
    )
