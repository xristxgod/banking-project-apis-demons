from django.utils.translation import gettext as _

from apps.orders.models import Payment, OrderStatus

from telegram.utils import make_text
from telegram.middlewares.request import Request

from telegram.bot_apps.orders import keyboards


def not_found_deposit(request: Request) -> dict:
    pass


def view_create_deposit_question(request: Request, payment_info: dict) -> dict:
    pass


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
