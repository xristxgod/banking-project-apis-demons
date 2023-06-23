from datetime import datetime

from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

from apps.telegram.bot_apps.utils import make_text
from apps.telegram.bot_apps.middlewares import UserData
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
            func=lambda call: call.data == 'back_to_menu',
        )

    def call(self, message: types.Message, user: UserData, cb_data: str) -> dict:
        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=keyboards.get_menu_keyboard(),
        )

    def without_auth_call(self, message: types.Message, from_user: types.User, cb_data: str) -> dict:
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
            config=callbacks.registration.filter(),
        )

    def call(self, message: types.Message, user: UserData, cb_data: str) -> dict:
        return dict(
            text=make_text(_(':smiling_face_with_halo: You are already registered!\n\n'
                             ':upwards_button: Select actions: :downwards_button:')),
            reply_markup=keyboards.get_menu_keyboard(),
        )

    @transaction.atomic()
    def without_auth_call(self, message: types.Message, from_user: types.User, cb_data: str) -> dict:
        from apps.users.models import User

        cb_data = callbacks.registration.parse(callback_data=cb_data)
        if cb_data['referral_code'] != utils.EMPTY_REF_CODE:
            # TODO когда добавится реферальрая система, то можно делать
            ...

        user = User.objects.create(
            chat_id=from_user.id,
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

    def call(self, message: types.Message, user: UserData, cb_data: str) -> dict:
        return dict(
            text=make_text(
                _('{date_now}\n'
                  ':dollar_banknote: Balance: ${balance}'),
                date_now=datetime.now(),
                balance=user.balance,
            ),
            reply_markup=keyboards.get_back_keyboard('back_to_menu'),
        )
