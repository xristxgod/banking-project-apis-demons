from telebot import types
from telebot.callback_data import CallbackData

from django.db import transaction
from django.utils.translation import gettext as _

from apps.orders.models import Payment, OrderStatus

from telegram.utils import make_text
from telegram.services import save_message
from telegram.middlewares.request import Request

from telegram.bot_apps.orders import keyboards
from telegram.bot_apps.orders import callbacks


def not_found_deposit() -> dict:
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(
        text=make_text(_(':money_bag: Create')),
        callback_data=callbacks.create_deposit.new(step=callbacks.CreateDepositStep.START, data=callbacks.empty),
    ))

    return dict(
        text=make_text(_(
            ":persevering_face: Sorry, we couldn't find this deposit!\n"
            ":partying_face: You can create a new one!"
        )),
        reply_markup=markup,
    )


def view_create_deposit_question(payment_info: dict, callback: CallbackData, extra: dict = None) -> dict:
    markup = keyboards.get_question_keyboard(callback=callback, extra=extra)
    return dict(
        text=make_text(_(
            ':eight_pointed_star: New deposit:\n\n'
            ':coin: You give: {amount} {currency}\n'
            ':coin: You get: {usdt_amount} USDT\n\n'
            ':dollar_banknote: At the USDT exchange rate: ${usdt_exchange_rate}\n'
            ':battery: Our commission: ${usdt_commission}\n\n'
            ':credit_card: Payment via: {typ}'
        ),
            currency=payment_info['currency'].verbose_telegram,
            amount=payment_info['amount'],
            usdt_amount=payment_info['usdt_amount'],
            usdt_exchange_rate=payment_info['usdt_exchange_rate'],
            usdt_commission=payment_info['usdt_commission'],
            typ=_('QR code') if payment_info['deposit_type'] == Payment.Type.DEPOSIT else _('Crypto Wallet')
        ),
        reply_markup=markup,
    )


def view_deposit(payment: Payment) -> dict:
    markup = keyboards.get_deposit_view_keyboard(payment)

    match payment.status:
        case OrderStatus.CREATED:
            text = _(
                ':money_bag: Deposit#:{payment_id}\n\n'
                ':coin: You give: {amount} {currency}\n'
                ':coin: You get: {usdt_amount} USDT\n\n'
                ':dollar_banknote: At the USDT exchange rate: ${usdt_exchange_rate}\n'
                ':battery: Our commission: ${usdt_commission}\n\n'
            )
        case OrderStatus.SENT:
            text = _(
                ':money_bag: Deposit#:{payment_id}\n\n'
                ':coin: You gave it away: {amount} {currency}\n'
                ":coin: You'll get: {usdt_amount} USDT\n\n"
                ':dollar_banknote: At the USDT exchange rate: ${usdt_exchange_rate}\n'
                ':battery: Our commission: ${usdt_commission}\n\n'
            )
        case OrderStatus.DONE:
            text = _(
                ':check_mark_button: DONE | Deposit#:{payment_id}\n\n'
                ':coin: You gave it away: {amount} {currency}\n'
                ':coin: You got: {usdt_amount} USDT\n\n'
                ':dollar_banknote: At the USDT exchange rate: ${usdt_exchange_rate}\n'
                ':battery: Our commission: ${usdt_commission}\n\n'
            )
        case OrderStatus.CANCEL:
            text = _(
                ':cross_mark: CANCEL | Deposit#:{payment_id}\n\n'
                ':coin: You would give: {amount} {currency}\n'
                ":coin: You'd get: {usdt_amount} USDT\n\n"
                ':dollar_banknote: At the USDT exchange rate: ${usdt_exchange_rate}\n'
                ':battery: Our commission: ${usdt_commission}\n\n'
            )
        case OrderStatus.ERROR:
            text = _(
                ':sos_button: ERROR | Deposit#:{payment_id}\n\n'
                ':coin: You would give: {amount} {currency}\n'
                ":coin: You'd get: {usdt_amount} USDT\n\n"
                ':dollar_banknote: At the USDT exchange rate: ${usdt_exchange_rate}\n'
                ':battery: Our commission: ${usdt_commission}\n\n'
                ':disappointed_face: An error has occurred, we apologize!'
            )
        case _:
            raise ValueError()

    return dict(
        text=make_text(
            text,
            payment_id=payment.pk,
            amount=payment.order.amount,
            currency=payment.order.currency.verbose_telegram,
            usdt_amount=payment.usdt_amount,
            usdt_exchange_rate=payment.usdt_exchange_rate,
            usdt_commission=payment.usdt_commission,
        ),
        reply_markup=markup,
    )


@transaction.atomic()
def view_active_deposit(payment: Payment, request: Request) -> dict:
    save_message(message_id=request.message_id + 1, obj=payment)
    return view_deposit(payment)


def view_last_deposit(payment: Payment) -> dict:
    return view_deposit(payment)


def view_deposit_history(request: Request) -> dict:
    from tabulate import tabulate

    deposits = request.user.deposit_history(10)
    if not deposits:
        return dict(
            text=make_text(_(
                ":hushed_face: You don't have a single deposit!"
            ))
        )

    markup = types.InlineKeyboardMarkup()

    if len(deposits) > 5:
        # TODO add download report
        markup.row()

    headers = (
        'PK', 'Amount', 'USDT Amount', 'Commission', 'Confirmed', 'Status',
    )

    table = []
    for deposit in deposits:
        table.append((
            deposit.pk,
            make_text('{amount} {currency}',
                      amount=deposit.order.amount,
                      currency=deposit.order.currency.verbose_telegram),
            make_text('${usdt_amount}',
                      usdt_amount=deposit.usdt_amount),
            make_text('${commission}',
                      commission=deposit.usdt_commission),
            deposit.order.confirmed,
            make_text(deposit.order.status_by_telegram),
        ))

    return dict(
        text=tabulate(table, headers=headers),
        reply_markup=markup,
    )


def not_found_withdraw(request: Request) -> dict:
    pass


def view_active_withdraw(payment: Payment) -> dict:
    pass


def view_last_withdraw(payment: Payment) -> dict:
    pass


def view_history_withdraw(payment: Payment) -> dict:
    pass
