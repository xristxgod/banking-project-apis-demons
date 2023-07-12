from telebot import types

from django.utils.translation import gettext as _

from src.caches.ram import cached

from apps.orders.models import OrderStatus, Payment
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

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_('Create deposit')),
        callback_data='create-deposit:step#0'
    ))

    return keyboard


@cached(60 * 30)
def get_currencies_keyboard(prefix: str) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    buttons = []
    for currency in Currency.objects.all():
        buttons.append(types.InlineKeyboardButton(
            text=make_text(_(currency.verbose_telegram)),
            callback_data=f'{prefix}:{currency.id}'
        ))

    keyboard.row(*buttons)

    return keyboard


def get_deposit_type_keyboard(prefix: str) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            text=make_text(_('By crypto wallet')),
            callback_data=f'{prefix}:{Payment.Type.BY_PROVIDER_DEPOSIT}',
        ),
        types.InlineKeyboardButton(
            text=make_text(_('By qr code')),
            callback_data=f'{prefix}:{Payment.Type.DEPOSIT}',
        ),
    )

    return keyboard


def get_question_keyboard(prefix: str) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            text=make_text(_('No')),
            callback_data=f'{prefix}:{callbacks.Answer.NO}',
        ),
        types.InlineKeyboardButton(
            text=make_text(_('Yes')),
            callback_data=f'{prefix}:{callbacks.Answer.YES}',
        ),
    )

    return keyboard
