import logging

import telebot

from django.conf import settings

from apps.telegram.bot_apps import filters
from apps.telegram.bot_apps import middlewares
from apps.telegram.bot_apps import APPS_HANDLERS


logger = telebot.logger
logger.setLevel(logging.ERROR)
logger.setLevel(logging.INFO)

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, use_class_middlewares=True)

# Setup middlewares
bot.setup_middleware(middlewares.TextParamsMiddleware())
bot.setup_middleware(middlewares.UserMiddleware())
# Setup filters
bot.add_custom_filter(filters.ConfigFilter())
# Setup apps
for handler in APPS_HANDLERS:
    handler(bot)
