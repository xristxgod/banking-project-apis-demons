from telebot import types

from django.utils.translation import gettext as _

from apps.telegram.bot_apps.base.keyboards import get_back_button
from apps.telegram.bot_apps.start.handlers import StartHandler
from apps.telegram.utils import make_text
from apps.telegram.middlewares.user import BaseUserData
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

    def call(self, message: types.Message, user: BaseUserData, cb_data: str) -> dict:
        markup = keyboards.get_orders_keyboard()
        if cb_data:
            markup.row(get_back_button(pattern='menu'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:\n\n'
                             'Quick deposit creation:\n'
                             '`/makedeposit <network>:<currency> <amount>`')),
            reply_markup=markup,
        )


class DepositHandlers(StartHandler):
    def registration_handlers(self):
        self.bot.register_message_handler(
            callback=self,
            commands=None,
            regexp=r'^/(make)?deposit( [A-z]+:[A-z]+ \d*[.,]?\d+)?$',
        )

    def call(self, message: types.Message, user: BaseUserData, cb_data: str) -> dict:
        pass