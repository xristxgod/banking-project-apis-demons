import logging

import telebot

from django.conf import settings

from telegram import middlewares, filters
from apps.telegram.bot_apps import APPS_HANDLERS

logger = telebot.logger
logger.setLevel(logging.ERROR)
logger.setLevel(logging.INFO)

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, use_class_middlewares=True)

# Setup middlewares
bot.setup_middleware(middlewares.UserMiddleware())
# Setup filters
bot.add_custom_filter(filters.CallbackQueryFilter())
bot.add_custom_filter(filters.RegexpFilter())
# Setup apps
for handler in APPS_HANDLERS:
    handler(bot)
