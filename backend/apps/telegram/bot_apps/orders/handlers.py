from telebot import types

from django.utils.translation import gettext as _

from apps.telegram.bot_apps.base.handlers import AbstractStepsMixin
from apps.telegram.bot_apps.base.keyboards import get_back_button
from apps.telegram.bot_apps.start.handlers import StartHandler
from apps.telegram.utils import make_text
from apps.telegram.middlewares.user import BaseUserData
from apps.telegram.bot_apps.orders import keyboards
from apps.telegram.bot_apps.orders import callbacks


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

    def call(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        markup = keyboards.get_orders_keyboard()
        if extra['cb_data']:
            markup.row(get_back_button(pattern='menu'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:\n\n'
                             'Quick deposit creation:\n'
                             '`/makedeposit <network>:<currency> <amount>`')),
            reply_markup=markup,
        )


class DepositHandlers(AbstractStepsMixin, StartHandler):
    def registration_handlers(self):
        self.bot.register_message_handler(
            callback=self,
            regexp=r'^/(make)?deposit( [A-z]+:[A-z]+ \d*[.,]?\d+)?$',
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'deposit',
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.deposit_answer.filter(),
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.deposit_step.filter(),
        )

    def call(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        if extra['cb_data'] == 'deposit' or len(message.text.split()) == 1:
            markup = keyboards.get_create_deposit_keyboard()
            if extra['cb_data']:
                markup.row(get_back_button(pattern='orders'))

            return dict(
                text=make_text(_('Do you want create order?\n\n...manual text...')),
                reply_markup=markup,
            )
        elif len(message.text.split()) > 1:
            # Fast create
            pass
