from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

from apps.telegram.bot_apps.base.keyboards import get_back_button
from apps.telegram.bot_apps.start.handlers import StartHandler
from apps.telegram.bot_apps.utils import make_text
from apps.telegram.bot_apps.middlewares import UserData
from apps.telegram.bot_apps.orders import keyboards


class OrderHandler(StartHandler):
    def registration_handlers(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['orders'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'orders',
        )

    def call(self, message: types.Message, user: UserData, cb_data: str) -> dict:
        markup = keyboards.get_orders_keyboard()
        if cb_data:
            markup.row(get_back_button(pattern='menu'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=markup,
        )
