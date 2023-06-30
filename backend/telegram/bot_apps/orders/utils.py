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
                         ':money_with_wings: {amount} {currency} => $ {usd_amount}\n\n'
                         ':dollar_banknote: USD rate: $ {usd_exchange_rate}\n'
                         ':receipt: Commission: $ {usd_commission}\n'
                         'Created: {created}\n\n'
                         '{status}')
            text = make_text(
                raw_text=raw_text,
                pk=deposit.pk,
                amount=deposit.order.amount,
                currency=deposit.order.currency.verbose_telegram,
                usd_exchange_rate=deposit.usd_exchange_rate,
                usd_commission=deposit.commission,
                created=deposit.order.created,
                status=deposit.status_by_telegram,
            )
        case OrderStatus.CANCEL:
            raw_text = _(':cross_mark: CANCEL Deposit: {pk}\n\n'
                         ':money_with_wings: {amount} {currency} => $ {usd_amount}\n\n'
                         ':dollar_banknote: USD rate: $ {usd_exchange_rate}\n'
                         ':receipt: Commission: $ {usd_commission}\n'
                         'Created: {created}')
            text = make_text(
                raw_text=raw_text,
                pk=deposit.pk,
                amount=deposit.order.amount,
                currency=deposit.order.currency.verbose_telegram,
                usd_exchange_rate=deposit.usd_exchange_rate,
                usd_commission=deposit.commission,
                created=deposit.order.created,
            )
        case OrderStatus.DONE:
            transaction = deposit.order.transaction
            raw_text = _(':check_mark_button: DONE Deposit: {pk}\n\n'
                         ':money_with_wings: {amount} {currency} => $ {usd_amount}\n\n'
                         ':dollar_banknote: USD rate: $ {usd_exchange_rate}\n'
                         ':receipt: Commission: $ {usd_commission}\n\n'
                         'Hash: {transaction_hash}\n'
                         ':receipt: Fee: {fee} {currency}\n'
                         'Sender: {sender}\n\n'
                         'Confirmed: {confirmed}')
            text = make_text(
                raw_text=raw_text,
                pk=deposit.pk,
                amount=deposit.order.amount,
                currency=deposit.order.currency.verbose_telegram,
                usd_exchange_rate=deposit.usd_exchange_rate,
                usd_commission=deposit.commission,
                transaction_hash=transaction.transaction_hash,
                fee=transaction.fee,
                sender=transaction.sender_address,
                confirmed=deposit.order.confirmed,
            )
        case _:
            text = make_text(_('Sorry, Not found!'))

    return dict(
        text=text,
        reply_markup=keyboards.get_orders_keyboard(request),
    )
