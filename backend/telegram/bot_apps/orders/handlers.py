from django.db import transaction
from django.utils.translation import gettext as _

from telegram.utils import make_text
from apps.telegram.bot_apps.base.keyboards import get_back_keyboard
from telegram.middlewares.request import TelegramRequest
from telegram.bot_apps.start.handlers import StartHandler

from telegram.bot_apps.orders import keyboards


class OrdersHandler(StartHandler):
    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['orders', 'order'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'orders',
        )

    def call(self, request: TelegramRequest) -> dict:
        markup = keyboards.get_orders_keyboard()
        if request.data:
            markup.row(get_back_keyboard('menu'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=markup,
        )
