from django.db import transaction

from apps.orders.models import Payment
from apps.orders.services import create_payment, cancel_payment

from telegram.services import del_message
from telegram.middlewares.request import Request
from telegram.bot_apps.orders.utils import view_deposit, view_active_deposit


@transaction.atomic()
def make_deposit(request: Request, deposit_info: dict) -> dict:
    payment = create_payment(
        user=request.user,
        typ=deposit_info.pop('deposit_type'),
        **deposit_info,
    )
    return view_active_deposit(payment, request)


@transaction.atomic()
def cancel_deposit(request: Request, payment: Payment) -> dict:
    cancel_payment(payment)
    del_message(payment)
    # TODO make task for update messages
    return view_deposit(payment)
