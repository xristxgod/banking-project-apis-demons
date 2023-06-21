from telebot import types

from apps.telegram.bot import bot


def start(message: types.Message, data: dict):
    bot.reply_to(message, f"Howdy, how are you doing? {data}")
