import telebot

from apps.telegram.bot_apps.start import handlers


def init_handlers(bot: telebot.TeleBot):
    bot.add_message_handler()
