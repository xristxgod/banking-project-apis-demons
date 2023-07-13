from typing import Optional

from telebot import types
from django.utils.translation import gettext as _

from telegram.utils import make_text


def get_registration_keyboard(ref_code: Optional[str] = None) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()

    callback_data = 'reg'
    if ref_code and len(ref_code) == 5:
        callback_data += f':{ref_code}'

    markup.row(types.InlineKeyboardButton(
        text=make_text(_(':check_mark_button: Register')),
        callback_data=callback_data,
    ))

    return markup


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
