from telebot import types

from django.utils.translation import gettext as _

from apps.orders.models import OrderStatus
from apps.cryptocurrencies.models import Currency

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
            callback_data='premakedeposit'
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
                    callback_data='cancel_deposit',
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


def get_deposit_question_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            text=make_text(_('No')),
            callback_data=callbacks.make_deposit_question.new(
                answer=callbacks.MakeDepositQuestion.NO,
            )
        ),
        types.InlineKeyboardButton(
            text=make_text(_('Yes')),
            callback_data=callbacks.make_deposit_question.new(
                answer=callbacks.MakeDepositQuestion.YES,
            )
        )
    )

    return keyboard


def get_currencies_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    buttons = []
    for currency in Currency.objects.all():
        buttons.append(types.InlineKeyboardButton(
            text=make_text(currency.verbose_telegram),
            callback_data=f'premakedeposit:currency-{currency.pk}'
        ))

    keyboard.row(*buttons)

    return keyboard
