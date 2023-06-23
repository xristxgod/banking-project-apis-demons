from telebot import types

from django.utils.translation import gettext as _

from apps.telegram.bot_apps.utils import make_text
from apps.telegram.bot_apps.start import utils
from apps.telegram.bot_apps.start import callbacks


def get_menu_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':money_bag: Balance')),
        callback_data='balance',
    ))

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':briefcase: Orders')),
        callback_data='orders',
    ))

    return keyboard


def get_registration_keyboard(message: types.Message) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()

    markup.row(types.InlineKeyboardButton(
        text=make_text(_(':check_mark_button: Register')),
        callback_data=callbacks.registration.new(
            referral_code=utils.get_referral_code(message),
        ),
    ))
    return markup
