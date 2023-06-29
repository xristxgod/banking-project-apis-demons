from telebot import types

from django.utils.translation import gettext as _

from apps.orders.models import OrderStatus, Deposit
from apps.telegram.utils import make_text
from apps.cryptocurrencies.models import Currency
from apps.telegram.bot_apps.orders import callbacks


def get_orders_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':briefcase: My orders')),
        callback_data='my_orders',
    ))

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':money_with_wings: Deposit')),
        callback_data='deposit'
    ))

    return keyboard


def get_create_deposit_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':money_with_wings: Create')),
        callback_data='deposit:create',
    ))

    return keyboard


def get_currencies_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    buttons = []
    for currency in Currency.objects.all():
        buttons.append(types.InlineKeyboardButton(
            text=make_text(currency.verbose_telegram),
            callback_data=f'deposit:currency:{currency.id}'
        ))

    keyboard.add(*buttons)

    return keyboard


def get_deposit_answer_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            text=make_text(_(':cross_mark_button:')),
            callback_data=callbacks.deposit_answer.new(answer=callbacks.Answer.NO),
        ),
        types.InlineKeyboardButton(
            text=make_text(_(':check_mark_button:')),
            callback_data=callbacks.deposit_answer.new(answer=callbacks.Answer.YES),
        ),
    )

    return keyboard


def get_deposit_keyboard(deposit: Deposit) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    if deposit.order.status == OrderStatus.CREATED:
        keyboard.row(
            types.InlineKeyboardButton(
                text=make_text(_(':eight_spoked_asterisk: To pay')),
                url=deposit.payment_url,
            ),
            types.InlineKeyboardButton(
                text=make_text(_(':cross_mark: Cancel')),
                callback_data=f'deposit:cancel:{deposit.pk}',
            )
        )
    elif deposit.order.status == OrderStatus.DONE:
        keyboard.row(
            types.InlineKeyboardButton(
                text=make_text(_(':receipt: Transaction')),
                url=deposit.transaction_url,
            ),
        )
        keyboard.row(
            types.InlineKeyboardButton(
                text=make_text(_(':counterclockwise_arrows_button: Repeat'))
            )
        )

    return keyboard
