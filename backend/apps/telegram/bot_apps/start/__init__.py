import telebot

from . import handlers
from . import callbacks


def init_handlers(bot: telebot.TeleBot):
    # Start handler
    bot.register_message_handler(
        callback=handlers.start,
        commands=['start', 'help']
    )

    # Registration handler
    bot.register_callback_query_handler(
        callback=handlers.registration,
        func=None,
        config=callbacks.registration.filter(),
    )
