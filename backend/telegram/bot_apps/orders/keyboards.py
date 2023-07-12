from telebot import types
from telebot.callback_data import CallbackData

from django.utils.translation import gettext as _

from src.caches.ram import cached

from apps.orders.models import OrderStatus, Order, Payment
from apps.cryptocurrencies.models import Currency

from telegram.utils import make_text
from telegram.middlewares.request import Request

from telegram.bot_apps.orders import callbacks


def get_orders_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':money_bag: Deposit')),
        callback_data=callbacks.deposit.new(type='menu'),
    ))

    keyboard.row(types.InlineKeyboardButton(
        text=make_text(_(':money_with_wings: Withdraw')),
        callback_data=callbacks.deposit.new(type='menu'),
    ))

    return keyboard


@cached(60 * 30)
def get_currencies_keyboard(callback: CallbackData, extra: dict = None) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    extra = extra or {}

    buttons = []
    for currency in Currency.objects.all():
        buttons.append(types.InlineKeyboardButton(
            text=make_text(_(currency.verbose_telegram)),
            callback_data=callback.new(data=currency.id, **extra),
        ))

    keyboard.row(*buttons)

    return keyboard


def get_deposit_type_keyboard(callback: CallbackData, extra: dict = None) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            text=make_text(_(':coin: By Crypto Wallet')),
            callback_data=callback.new(data=Payment.Type.BY_PROVIDER_DEPOSIT, **extra),
        ),
        types.InlineKeyboardButton(
            text=make_text(_('By QR code')),
            callback_data=callback.new(data=Payment.Type.DEPOSIT, **extra),
        ),
    )

    return keyboard


def get_question_keyboard(callback: CallbackData, extra: dict = None) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            text=make_text(_(':cross_mark:')),
            callback_data=callback.new(data=callbacks.Answer.NO, **extra),
        ),
        types.InlineKeyboardButton(
            text=make_text(_(':check_mark_button:')),
            callback_data=callback.new(data=callbacks.Answer.YES, **extra),
        ),
    )

    return keyboard


def get_deposit_menu_keyboard(request: Request) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    active_deposit = request.user.active_deposit
    last_deposit = request.user.last_deposit

    if active_deposit:
        keyboard.row(types.InlineKeyboardButton(
            text=make_text(_(':green_circle: Active')),
            callback_data=callbacks.deposit.new(type=callbacks.PaymentType.ACTIVE)
        ))
    else:
        keyboard.row(types.InlineKeyboardButton(
            text=make_text(_(':blue_circle: Create')),
            callback_data=callbacks.create_deposit.new(step=callbacks.CreateDepositStep.START, data=callbacks.empty),
        ))

    if active_deposit != last_deposit:
        keyboard.row(types.InlineKeyboardButton(
            text=make_text(_(':yellow_circle: Last')),
            callback_data=callbacks.deposit.new(type=callbacks.PaymentType.LAST),
        ))

    return keyboard


def get_deposit_view_keyboard(payment: Payment) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()

    if payment.status == OrderStatus.CREATED:
        keyboard.row(
            types.InlineKeyboardButton(
                text=make_text(_(':cross_mark: Cancel')),
                callback_data=callbacks.cancel_payment.new(pk=payment.pk),
            ),
            types.InlineKeyboardButton(
                text=make_text(_(':credit_card: To pay')),
                url=payment.url,
            ),
        )

    if payment.status in Order.DONE_STATUSES:
        keyboard.row(
            types.InlineKeyboardButton(
                text=make_text(_(':counterclockwise_arrows_button: Repeat')),
                callback_data=callbacks.repeat_deposit.new(pk=payment.pk),
            )
        )

    if payment.status == OrderStatus.DONE:
        keyboard.row(
            types.InlineKeyboardButton(
                text=make_text(_(':receipt: View transaction')),
                url=payment.order.transaction.url,
            )
        )

    return keyboard
