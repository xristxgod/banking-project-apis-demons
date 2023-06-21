import telebot

import settings
from apps.telegram.bot_apps import init_webhook

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
# Init webhook
init_webhook(bot)
