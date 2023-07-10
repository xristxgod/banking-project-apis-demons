from telebot import types

from django.utils.translation import gettext as _

from apps.orders.models import OrderStatus
from apps.cryptocurrencies.models import Currency

from telegram.utils import make_text
from telegram.middlewares.request import Request

from telegram.bot_apps.orders import callbacks


def get_orders_keyboard(request: Request) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':briefcase: My orders')),
        callback_data='my_orders',
    ))

    return keyboard
