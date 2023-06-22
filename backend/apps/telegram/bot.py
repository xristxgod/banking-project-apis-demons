import telebot

from django.conf import settings


def init(_bot: telebot.TeleBot):
    # Init bot apps
    from apps.telegram import bot_apps
    bot_apps.init_apps(_bot)


bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, use_class_middlewares=True)
init(bot)
