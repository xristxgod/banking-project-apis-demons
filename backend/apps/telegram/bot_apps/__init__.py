import telebot

from . import start
from .middlewares import UserMiddleware


def init_apps(bot: telebot.TeleBot):
    bot.setup_middleware(UserMiddleware())
    start.init_handlers(bot)

