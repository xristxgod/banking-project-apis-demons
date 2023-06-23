from telebot import types

from django.utils.translation import gettext as _

from apps.telegram.bot_apps.utils import make_text


def get_orders_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':briefcase: My orders')),
        callback_data='my_orders',
    ))

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':money_with_wings: Deposit')),
        callback_data='deposit',
    ))

    return keyboard
