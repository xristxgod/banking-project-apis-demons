import telebot

from . import start
from .middlewares import UserMiddleware
from .filters import ConfigFilter


def init_apps(bot: telebot.TeleBot):
    bot.setup_middleware(UserMiddleware())
    bot.add_custom_filter(ConfigFilter())
    start.init_handlers(bot)
