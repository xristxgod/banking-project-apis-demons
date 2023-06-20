import telebot

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

import settings
from apps.telegram.bot_middlewares import UserMiddleware
from apps.telegram.bot_apps import init_apps, init_webhook

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
bot.add_middleware_handler(UserMiddleware())

init_webhook(bot)       # Set webhook
init_apps(bot)          # Init bot apps


class UpdateBot(APIView):
    def post(self, request: Request):
        json_str = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return Response(status=status.HTTP_201_CREATED)
