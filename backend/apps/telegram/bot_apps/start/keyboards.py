from typing import Optional
from telebot import types

from django.utils.translation import gettext as _

from apps.telegram.bot_apps.utils import make_text
from apps.telegram.bot_apps.start import utils
from apps.telegram.bot_apps.start import callbacks


def get_back_button(pattern: str) -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(
        text=make_text(_(':back_arrow: Back')),
        callback_data=pattern,
    )


def get_back_keyboard(patten: str, keyboard: Optional[types.InlineKeyboardMarkup] = None) -> types.InlineKeyboardMarkup:
    button = get_back_button(patten)
    if not keyboard:
        keyboard = types.InlineKeyboardMarkup()

    keyboard.row(button)

    return keyboard


def get_menu_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':money_bag: Balance')),
        callback_data='balance',
    ))

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':money_with_wings: Deposit')),
        callback_data='deposit',
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
