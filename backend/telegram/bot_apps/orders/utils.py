from django.utils.translation import gettext as _

from apps.orders.models import OrderStatus

from telegram.utils import make_text
from telegram.middlewares.request import TelegramRequest

from telegram.bot_apps.orders import keyboards


def view_active_deposit(request: TelegramRequest) -> dict:
    deposit = request.user.deposit

    match deposit.status:
        case OrderStatus.CREATED | OrderStatus.SENT:
            raw_text = _('Deposit: {pk}\n\n'
                         ':money_with_wings: {amount} {currency} => $ {usdt_amount}\n\n'
                         ':dollar_banknote: USDT rate: $ {usdt_exchange_rate}\n'
                         ':receipt: USDT Commission: $ {usdt_commission}\n'
                         'Created: {created}\n\n'
                         '{status}')
            text = make_text(
                raw_text=raw_text,
                pk=deposit.pk,
                amount=deposit.order.amount,
                currency=deposit.order.currency.verbose_telegram,
                usdt_amount=deposit.usdt_amount,
                usdt_exchange_rate=deposit.usdt_exchange_rate,
                usdt_commission=deposit.usdt_commission,
                created=deposit.order.created,
                status=deposit.status_by_telegram,
            )
        case OrderStatus.CANCEL:
            raw_text = _(':cross_mark: CANCEL Deposit: {pk}\n\n'
                         ':money_with_wings: {amount} {currency} => $ {usdt_amount}\n\n'
                         ':dollar_banknote: USDT rate: $ {usdt_exchange_rate}\n'
                         ':receipt: USDT Commission: $ {usdt_commission}\n\n'
                         'Created: {created}')
            text = make_text(
                raw_text=raw_text,
                pk=deposit.pk,
                amount=deposit.order.amount,
                currency=deposit.order.currency.verbose_telegram,
                usdt_amount=deposit.usdt_amount,
                usdt_exchange_rate=deposit.usdt_exchange_rate,
                usdt_commission=deposit.usdt_commission,
                created=deposit.order.created,
            )
        case OrderStatus.DONE:
            transaction = deposit.order.transaction
            raw_text = _(':check_mark_button: DONE Deposit: {pk}\n\n'
                         ':money_with_wings: {amount} {currency} => $ {usdt_amount}\n\n'
                         ':dollar_banknote: USDT rate: $ {usdt_exchange_rate}\n'
                         ':receipt: USDT Commission: $ {usdt_commission}\n\n'
                         'Hash: {transaction_hash}\n'
                         ':receipt: Fee: {fee} {currency}\n'
                         'Sender: {sender}\n\n'
                         'Confirmed: {confirmed}')
            text = make_text(
                raw_text=raw_text,
                pk=deposit.pk,
                amount=deposit.order.amount,
                currency=deposit.order.currency.verbose_telegram,
                usdt_amount=deposit.usdt_amount,
                usdt_exchange_rate=deposit.usdt_exchange_rate,
                usdt_commission=deposit.usdt_commission,
                transaction_hash=transaction.transaction_hash,
                fee=transaction.fee,
                sender=transaction.sender_address,
                confirmed=deposit.order.confirmed,
            )
        case _:
            text = make_text(_('Sorry, Not found!'))

    return dict(
        text=text,
        reply_markup=keyboards.get_deposit_keyboard(request),
    )


def view_question_deposit(deposit_info: dict) -> dict:
    return dict(
        text=make_text(
            raw_text=_(':round_pushpin: Deposit info:\n\n'
                       ':money_with_wings: You give: {amount} {currency}\n'
                       ':money_bag: You get: $ {usdt_amount}\n\n'
                       ':dollar_banknote: USDT rate: $ {usdt_rate_cost}\n'
                       ':receipt: USDT Commission: $ {usdt_commission}'),
            amount=deposit_info['amount'],
            currency=deposit_info['currency'].verbose_telegram,
            usdt_amount=deposit_info['usdt_amount'],
            usdt_rate_cost=deposit_info['usdt_rate_cost'],
            usdt_commission=deposit_info['usdt_commission'],
        ),
        reply_markup=keyboards.get_deposit_question_keyboard(),
    )
