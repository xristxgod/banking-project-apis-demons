from telebot import types

from django.utils.translation import gettext as _

from apps.orders.models import OrderStatus

from telegram.utils import make_text
from telegram.middlewares.request import TelegramRequest

from telegram.bot_apps.orders import callbacks


def get_orders_keyboard(request: TelegramRequest) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':briefcase: My orders')),
        callback_data='my_orders',
    ))

    if request.user.has_active_deposit:
        keyboard.row(types.InlineKeyboardButton(
            text=make_text(_(':money_with_wings: Active Deposit')),
            callback_data='deposit',
        ))
    else:
        keyboard.row(types.InlineKeyboardButton(
            text=make_text(_(':money_with_wings: Make Deposit')),
            callback_data='make_deposit'
        ))

    return keyboard


def get_deposit_keyboard(request: TelegramRequest) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    deposit = request.user.deposit
    match deposit.status:
        case OrderStatus.CREATED:
            # todo
            keyboard.row(
                types.InlineKeyboardButton(
                    text=_('Cancel'),
                    callback_data='cancle',
                ),
                types.InlineKeyboardButton(
                    text=_('To pay'),
                    url=deposit.payment_url,
                ),
            )
        case OrderStatus.DONE:
            keyboard.row(
                types.InlineKeyboardButton(
                    text=_('View in blockchain'),
                    url=deposit.transaction_url,
                ),
                types.InlineKeyboardButton(
                    text=_('Repeat'),
                    callback_data=callbacks.repeat_deposit.new(pk=deposit.pk)
                )
            )

    return keyboard
