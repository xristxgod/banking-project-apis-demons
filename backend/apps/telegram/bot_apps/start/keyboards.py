from telebot import types

from django.utils.translation import gettext as _


def get_menu_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton(
        text=_('Balance'),
        callback_data='balance',
    ))

    return keyboard
