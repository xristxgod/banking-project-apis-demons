from django.db import transaction

from apps.orders.services import create_payment

from telegram.middlewares.request import Request
from telegram.bot_apps.orders.utils import view_active_deposit


@transaction.atomic()
def make_deposit(request: Request, deposit_info: dict) -> dict:
    payment = create_payment(
        user=request.user,
        typ=deposit_info.pop('deposit_type'),
        **deposit_info,
    )
    return view_active_deposit(payment, request)
