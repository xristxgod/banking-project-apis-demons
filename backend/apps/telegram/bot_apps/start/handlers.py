from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

from apps.telegram.bot import bot
from apps.users.models import User
from apps.telegram.bot_apps.start import keyboards
from apps.telegram.bot_apps.start import callbacks

EMPTY_REF_CODE = 'empty'


def _get_referral_code(text: str):
    arr = text.split()
    if len(arr) == 2:
        return arr[1]
    return EMPTY_REF_CODE


def start(message: types.Message, data: dict):
    if user := data['user']:
        text = _('Hi, {username}').format(username=user.username)
        markup = keyboards.get_menu_keyboard()
    else:
        text = _('Pls, Registration')
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(
            text=_('Registration'),
            callback_data=callbacks.registration.new(referral_code=_get_referral_code(message.text)),
        ))
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=markup,
    )


@transaction.atomic()
def registration(cq: types.CallbackQuery):
    # TODO Это на потом
    callback_data: dict[str: str] = callbacks.registration.parse(callback_data=cq.data)
    if callback_data['referral_code'] != EMPTY_REF_CODE:
        # TODO когда добавится реферальрая система, то можно делать
        pass

    user = User.objects.create(
        chat_id=cq.from_user.id,
        username=cq.from_user.username,
    )
    bot.edit_message_text(
        chat_id=user.chat_id,
        text=_('Welcome, {username}').format(username=user.username),
        message_id=cq.message.message_id,
    )
