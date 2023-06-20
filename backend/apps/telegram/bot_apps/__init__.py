import telebot

import settings
from apps.telegram.bot_apps import start


def init_webhook(bot: telebot.TeleBot):
    webhook = bot.get_webhook_info()
    if webhook.url != settings.TELEGRAM_WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=settings.TELEGRAM_WEBHOOK_URL)


def init_apps(bot: telebot.TeleBot):
    start.init_handlers(bot)       # Common app
