import telebot

from . import handlers


def init_handlers(bot: telebot.TeleBot):
    # Deposit handler
    bot.register_message_handler(
        callback=handlers.deposit,
        commands=['deposit'],
    )
    bot.register_callback_query_handler(
        callback=handlers.deposit,
        func=lambda call: call == 'deposit',
    )
