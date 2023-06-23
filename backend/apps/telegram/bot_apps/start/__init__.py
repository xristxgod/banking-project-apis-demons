import telebot

from . import handlers
from . import callbacks


def _init_sub_handlers(bot: telebot.TeleBot):
    # Back to menu
    bot.register_callback_query_handler(
        callback=handlers.start,
        func=lambda call: call.data == 'back_to_menu'
    )


def init_handlers(bot: telebot.TeleBot):
    # Start handler
    bot.register_message_handler(
        callback=handlers.start,
        commands=['start', 'help'],
    )

    # Registration handler
    bot.register_callback_query_handler(
        callback=handlers.registration,
        func=None,
        config=callbacks.registration.filter(),
    )

    # Balance handler
    bot.register_callback_query_handler(
        callback=handlers.balance,
        func=lambda call: call.data == 'balance',
    )

    _init_sub_handlers(bot)
