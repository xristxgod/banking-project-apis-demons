from telebot.callback_data import CallbackData
from django.utils.translation import gettext as _

from apps.orders.models import Payment, OrderStatus

from telegram.utils import make_text
from telegram.middlewares.request import Request

from telegram.bot_apps.orders import keyboards


def not_found_deposit(request: Request) -> dict:
    pass


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


def view_active_deposit(payment: Payment) -> dict:
    pass


def view_last_deposit(payment: Payment) -> dict:
    pass


def view_history_deposit(payment: Payment) -> dict:
    pass


def not_found_withdraw(request: Request) -> dict:
    pass


def view_active_withdraw(payment: Payment) -> dict:
    pass


def view_last_withdraw(payment: Payment) -> dict:
    pass


def view_history_withdraw(payment: Payment) -> dict:
    pass
