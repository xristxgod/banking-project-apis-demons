from typing import Optional

from django.db import transaction
from django.utils.translation import gettext as _

from telegram.utils import make_text
from telegram.bot_apps.base.handlers import AbstractHandler
from telegram.bot_apps.base.keyboards import get_back_keyboard
from telegram.middlewares.request import Request

from telegram.bot_apps.start import keyboards


class StartHandler(AbstractHandler):
    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['start'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'menu',
        )

    def call_without_auth(self, request: Request) -> dict:
        return dict(
            text=make_text(_(
                ':waving_hand: You are not registered!\n'
                ':heart_hands: To join us, click on:'
            )),
            reply_markup=keyboards.get_registration_keyboard(request.text_params),
        )

    def call(self, request: Request) -> dict:
        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=keyboards.get_menu_keyboard(),
        )


class RegistrationHandler(StartHandler):
    @classmethod
    def get_referral_code(cls, reqeust: Request) -> Optional[str]:
        if len(reqeust.data) == 9:
            return reqeust.data.replace('reg:', '')
        elif reqeust.has_text_params:
            return reqeust.text_params

    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            regexp=r'^/reg( \w{5})?$',
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data.startswith('reg')
        )

    @transaction.atomic()
    def call_without_auth(self, request: Request) -> dict:
        from apps.users.models import User

        if referral_code := self.get_referral_code(request):
            # TODO
            pass

        user = User.objects.create(
            id=request.user.id,
            username=request.user.username,
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
    cb_data_startswith = 'balance'

    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['balance'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data.startswith(self.cb_data_startswith),
        )

    def call(self, request: Request) -> dict:
        markup = get_back_keyboard('menu') if request.data else None
        return dict(
            text=make_text(
                _(':dollar_banknote: Balance: ${balance}'),
                balance=request.user.balance,
            ),
            reply_markup=markup,
        )
