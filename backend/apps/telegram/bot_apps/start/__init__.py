import telebot

from . import handlers


def init_handlers(bot: telebot.TeleBot):
    # Start handler
    bot.register_message_handler(
        callback=handlers.start,
        commands=['start', 'help']
    )
