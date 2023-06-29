import decimal
import datetime
from typing import Optional

from telebot import types

from django.utils.translation import gettext as _

from apps.orders.models import Deposit
from apps.orders.services import calculate_deposit_amount, create_deposit_by_telegram, cancel_deposit
from apps.cryptocurrencies.models import Currency
from apps.telegram.bot_apps.base.handlers import AbstractStepsMixin
from apps.telegram.bot_apps.base.keyboards import get_back_button, get_back_keyboard
from apps.telegram.bot_apps.start.handlers import StartHandler
from apps.telegram.utils import make_text
from apps.telegram.middlewares.user import BaseUserData
from apps.telegram.bot_apps.orders import keyboards
from apps.telegram.bot_apps.orders import callbacks


class OrderHandler(StartHandler):
    def registration_handlers(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['orders'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'orders',
        )

    def call(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        markup = keyboards.get_orders_keyboard()
        if extra['cb_data']:
            markup.row(get_back_button(pattern='menu'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=markup,
        )


class DepositHandlers(AbstractStepsMixin, StartHandler):
    def registration_handlers(self):
        self.bot.register_message_handler(
            callback=self,
            regexp=r'^/deposit( [A-z]+:[A-z]+ \d*[.,]?\d+)?$',
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data.startswith('deposit'),
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.deposit_answer.filter(),
        )

    def make_answer_message(self, user: BaseUserData):
        self.storage[user.chat_id].update(calculate_deposit_amount(
            user=user.obj,
            **self.storage[user.chat_id],
        ))

        return dict(
            text=make_text(
                _(':round_pushpin: Deposit info:\n\n'
                  ':money_with_wings: You give: {amount} {currency}\n'
                  ':money_bag: You get: $ {usd_amount}\n\n'
                  ':dollar_banknote: USD rate: $ {usd_rate}\n'
                  ':receipt: Commission: $ {usd_commission}'),
                **self.storage[user.chat_id],
            ),
            reply_markup=keyboards.get_deposit_answer_keyboard(),
        )

    @classmethod
    def make_deposit_message(cls, deposit: Deposit):
        markup = keyboards.get_deposit_keyboard(deposit)

        return dict(
            text=make_text(_(':id_button: {pk}\n\n'
                             ':money_with_wings: {amount} {currency} => $ {usd_amount}\n'
                             ':dollar_banknote: USD rate: $ {usd_rate}\n'
                             ':receipt: Commission: $ {usd_commission}\n\n'
                             '{status}'),
                           pk=deposit.pk,
                           amount=deposit.order.amount,
                           currency=deposit.order.currency,
                           usd_amount=deposit.amount,
                           usd_rate=deposit.usd_exchange_rate,
                           usd_commission=deposit.commission,
                           status=deposit.order.status_by_telegram),
            reply_markup=markup,
        )

    def _pre_call(self, message: types.Message, user: BaseUserData, extra: dict) -> Optional[dict]:
        if extra['cb_data'].startswith('deposit:cancel:'):
            if cancel_deposit(user.obj, pk=int(extra['cb_data'].replace('deposit:cancel:', ''))):
                return dict(
                    text=make_text(':cross_mark: CANCELED! ' + message.text),
                )
            return dict(
                text=message.text,
            )
        if deposit := user.active_deposit:
            return self.make_deposit_message(deposit)

    def call(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        if params := self._pre_call(message, user, extra):
            return params

        if 'deposit' in (extra['cb_data'], message.text[1:]):
            markup = keyboards.get_create_deposit_keyboard()
            if extra['cb_data']:
                markup.row(get_back_button(pattern='orders'))

            return dict(
                text=make_text(_(':money_with_wings: Do you want to make a deposit?\n\n'
                                 ':page_with_curl: Instruction manual:\n\n'
                                 ':one: Choose a currency\n'
                                 ':two: Enter the amount:\n\n'
                                 ':receipt: We will calculate the `USD` exchange rate and commission, '
                                 'and then you can pay!\n\n'
                                 ':high_voltage: Create a deposit by command:\n'
                                 '`/deposit <network>:<currency> <amount>`')),
                reply_markup=markup,
            )

        return self._post_call(message, user, extra)

    def _post_call(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        if not self.storage.get(user.chat_id):
            return dict(
                text=make_text(_(":disappointed_face: Sorry, but, I'm not found!")),
                reply_markup=get_back_keyboard(patten='deposit'),
            )

        match callbacks.deposit_answer.parse(extra['cb_data'])['answer']:
            case callbacks.Answer.NO:
                del self.storage[user.chat_id]
                return dict(
                    text=make_text(_(":OK_hand: I've closed your deposit!")),
                    reply_markup=get_back_keyboard(patten='deposit'),
                )
            case callbacks.Answer.YES:
                return self.make_deposit_message(
                    deposit=create_deposit_by_telegram(
                        user=user.obj,
                        deposit_info=self.storage.pop(user.chat_id),
                    ),
                )

    def is_step(self, extra: dict) -> bool:
        return (
                extra['data'].get('step') or
                extra['cb_data'] == 'deposit:create' or
                extra['cb_data'].startswith('deposit:currency:')
        )

    def call_step(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        if extra['cb_data'] == 'deposit:create':
            markup = keyboards.get_currencies_keyboard()
            markup.add(get_back_button('deposit'))

            return dict(
                text=make_text(_(':yellow_circle: Choose a currency:')),
                reply_markup=markup,
            )
        elif extra['cb_data'].startswith('deposit:currency:'):
            self.storage[user.chat_id] = {
                'currency': Currency.objects.get(
                    pk=int(extra['cb_data'].replace('deposit:currency:', ''))
                ),
            }
            return dict(
                text=make_text(_(':fountain_pen: Write amount:\n\n'
                                 'Example:\n\t`100.2`\n\t`12,244`')),
                for_step=dict(
                    message=message,
                    callback=self,
                    data={
                        'user': user,
                        'step': 'wrote_amount',
                        'cb_data': 'cb_data',
                    }
                )
            )
        elif extra['data']['step'] == 'wrote_amount':
            try:
                self.storage[user.chat_id].update({
                    'amount': self.storage[user.chat_id]['currency'].str_to_decimal(message.text),
                })
                return self.make_answer_message(user)
            except decimal.InvalidOperation:
                del self.storage[user.chat_id]
                return dict(
                    text=make_text(_(':no_entry: Invalid amount :no_entry:\n'))
                )

