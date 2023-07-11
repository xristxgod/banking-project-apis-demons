from django.utils.translation import gettext as _

from apps.orders.models import Payment, OrderStatus

from telegram.utils import make_text
from telegram.middlewares.request import Request

from telegram.bot_apps.orders import keyboards


def not_found_deposit(request: Request) -> dict:
    pass


def view_create_deposit_question(payment_info: dict, prefix: str) -> dict:
    markup = keyboards.get_question_keyboard(prefix=prefix)
    return dict(
        text=make_text(_(
            f'Do you want create, {payment_info}',
        )),
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
