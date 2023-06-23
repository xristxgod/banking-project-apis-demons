from typing import Optional
from telebot import types

from django.utils.translation import gettext as _

from apps.telegram.bot_apps.utils import make_text


def get_back_button(pattern: str) -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(
        text=make_text(_(':left_arrow: Back')),
        callback_data=pattern,
    )


def get_back_keyboard(patten: str, keyboard: Optional[types.InlineKeyboardMarkup] = None) -> types.InlineKeyboardMarkup:
    button = get_back_button(patten)
    if not keyboard:
        keyboard = types.InlineKeyboardMarkup()

    keyboard.row(button)

    return keyboard
