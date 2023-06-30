from telebot import types
from django.db import transaction
from django.utils.translation import gettext as _

from apps.orders.models import OrderStatus

from telegram.utils import make_text
from telegram.bot_apps.base.keyboards import get_back_button
from telegram.middlewares.request import TelegramRequest
from telegram.bot_apps.start.handlers import StartHandler

from telegram.bot_apps.orders import utils
from telegram.bot_apps.orders import keyboards
from telegram.bot_apps.orders import callbacks


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
        markup = keyboards.get_orders_keyboard(request)
        if request.data:
            markup.row(get_back_button('menu'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=markup,
        )


class DepositHandler(StartHandler):
    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['deposit', 'mydeposit', 'activedeposit'],
        )

        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'deposit',
        )

    def view_active_deposit(self, request: TelegramRequest):
        # TODO add save message_id for further modification
        return utils.view_active_deposit(request)

    def call(self, request: TelegramRequest) -> dict:
        if not request.user.has_active_deposit:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(
                text=make_text(_('Create')),
                callback_data='makedeposit'
            ))

            return dict(
                text=make_text(_('You have a gntu of an active deposit')),
                reply_markup=markup,
            )

        return self.view_active_deposit(request)


class MakeDepositHandler(DepositHandler):
    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            regexp=r'^/makedeposit( [A-z]+:[A-z]+ \d*[.,]?\d+)?$',
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'makedeposit',
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.repeat_deposit.filter(),
        )

    def call(self, request: TelegramRequest) -> dict:
        # 1. Если у юзера есть активный депозит, то вернем его
        # 2. Если в тексте есть параметры то смотрим на них и если валидны сохраняем их в хранилище и даем ему
        #    две кнопки, да или нет
        # 3. Если пришел по repeat_deposit то создаем без вопросов и возвращаем ему новое сообщение (не меняем старое)

        if request.user.has_active_deposit:
            return self.view_active_deposit(request)
