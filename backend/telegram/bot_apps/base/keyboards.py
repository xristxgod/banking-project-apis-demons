from typing import Optional
from telebot import types

from django.utils.translation import gettext as _

from apps.telegram.utils import make_text


def get_back_button(callback_data: str) -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(
        text=make_text(_(':left_arrow: Back')),
        callback_data=callback_data,
    )


def get_back_keyboard(callback_data: str) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(get_back_button(callback_data))
    return keyboard
