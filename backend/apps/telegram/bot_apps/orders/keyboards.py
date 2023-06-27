from telebot import types

from django.utils.translation import gettext as _

from apps.telegram.bot_apps.utils import make_text
from apps.telegram.bot_apps.orders import callbacks


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


def get_pre_make_deposit_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.row(
        types.InlineKeyboardButton(
            text=make_text(_('No')),
            callback_data=callbacks.pre_make_deposit.new(answer='no'),
        ),
        types.InlineKeyboardButton(
            text=make_text(_('Yes')),
            callback_data=callbacks.pre_make_deposit.new(answer='yes'),
        )
    )

    return keyboard
