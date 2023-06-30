from datetime import datetime

from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

from apps.telegram.utils import make_text
from telegram.middlewares import BaseUserData
from apps.telegram.bot_apps.start import utils
from apps.telegram.bot_apps.start import keyboards
from apps.telegram.bot_apps.start import callbacks

from apps.telegram.bot_apps.base.handlers import AbstractHandler


class StartHandler(AbstractHandler):
    def registration_handlers(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['start', 'help'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data in ['menu', 'start'],
        )

    def call(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=keyboards.get_menu_keyboard(),
        )

    def call_without_auth(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        return dict(
            text=make_text(_(
                ':waving_hand: Welcome!\n'
                ':heart_hands: To join us, click on:'
            )),
            reply_markup=keyboards.get_registration_keyboard(message),
        )


class RegistrationHandler(AbstractHandler):
    def registration_handlers(self):
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.registration.filter(),
        )

    def call(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        return dict(
            text=make_text(_(':smiling_face_with_halo: You are already registered!\n\n'
                             ':upwards_button: Select actions: :downwards_button:')),
            reply_markup=keyboards.get_menu_keyboard(),
        )

    @transaction.atomic()
    def call_without_auth(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        from apps.users.models import User

        cb_data = callbacks.registration.parse(callback_data=extra['cb_data'])
        if cb_data['referral_code'] != utils.EMPTY_REF_CODE:
            # TODO когда добавится реферальрая система, то можно делать
            ...

        user = User.objects.create(
            id=user.chat_id,
            username=message.from_user.username,
        )

        return dict(
            text=make_text(
                _(':heart_on_fire: Registration was successful!\n'
                  '{username}, welcome to us!\n\n'
                  ':upwards_button: Select actions: :downwards_button:'),
                username=user.username,
            ),
            reply_markup=keyboards.get_menu_keyboard(),
        )


class BalanceHandler(StartHandler):
    def registration_handlers(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['balance'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'balance',
        )

    def call(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        from apps.telegram.bot_apps.base.keyboards import get_back_keyboard

        markup = get_back_keyboard('menu') if extra['cb_data'] else None
        return dict(
            text=make_text(
                _('{date_now}\n'
                  ':dollar_banknote: Balance: ${balance}'),
                date_now=datetime.now(),
                balance=user.balance,
            ),
            reply_markup=markup,
        )
