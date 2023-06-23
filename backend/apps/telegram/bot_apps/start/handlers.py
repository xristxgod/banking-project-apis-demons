from datetime import datetime

from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

from apps.telegram.bot import bot
from apps.users.models import User
from apps.telegram.bot_apps.utils import make_text
from apps.telegram.bot_apps.start import utils
from apps.telegram.bot_apps.start import keyboards
from apps.telegram.bot_apps.start import callbacks


def start(message: types.Message, data: dict):
    if data['user']:
        text = make_text(_(':upwards_button: Select actions: :downwards_button:'))
        markup = keyboards.get_menu_keyboard()
    else:
        text = make_text(_(
            ':waving_hand: Welcome!\n'
            ':heart_hands: To join us, click on:'
        ))
        markup = keyboards.get_registration_keyboard(message)

    bot.send_message(
        chat_id=message.from_user.id,
        text=text,
        reply_markup=markup,
    )


@transaction.atomic()
def registration(cq: types.CallbackQuery):
    # TODO Это на потом
    callback_data: dict[str: str] = callbacks.registration.parse(callback_data=cq.data)
    if callback_data['referral_code'] != utils.EMPTY_REF_CODE:
        # TODO когда добавится реферальрая система, то можно делать
        pass

    user = User.objects.create(
        chat_id=cq.from_user.id,
        username=cq.from_user.username,
    )

    bot.edit_message_text(
        chat_id=user.chat_id,
        text=make_text(
            _(':heart_on_fire: Registration was successful!\n'
              '{username}, welcome to us!\n\n'
              ':upwards_button: Select actions: :downwards_button:'),
            username=user.username,
        ),
        message_id=cq.message.message_id,
        reply_markup=keyboards.get_menu_keyboard(),
    )


def balance(cq: types.CallbackQuery, data: dict):
    user = data['user']
    bot.edit_message_text(
        chat_id=user.chat_id,
        text=make_text(
            _('{date_now}\n'
              ':dollar_banknote: Balance: ${balance}'),
            date_now=datetime.now(),
            balance=user.balance,
        ),
        message_id=cq.message.message_id,
    )
