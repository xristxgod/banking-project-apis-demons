import datetime
import decimal

from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

from apps.orders.services import calculate_deposit_amount, create_deposit_by_telegram, cancel_deposit
from apps.cryptocurrencies.models import Currency
from apps.telegram.bot_apps.base.handlers import AbstractStepsMixin
from apps.telegram.bot_apps.base.keyboards import get_back_button
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
            text=make_text(_(':upwards_button: Select actions: :downwards_button:\n\n'
                             'Quick deposit creation:\n'
                             '`/makedeposit <network>:<currency> <amount>`')),
            reply_markup=markup,
        )


class DepositHandlers(AbstractStepsMixin, StartHandler):
    def registration_handlers(self):
        self.bot.register_message_handler(
            callback=self,
            regexp=r'^/(make)?deposit( [A-z]+:[A-z]+ \d*[.,]?\d+)?$',
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
        deposit_info = self.storage[user.chat_id]

        self.storage[user.chat_id].update(calculate_deposit_amount(
            user=user.obj,
            amount=deposit_info['amount'],
            currency=deposit_info['currency'],
        ))

        markup = keyboards.get_deposit_answer_keyboard()

        return dict(
            text=make_text(
                _('Deposit: {now}\n\n'
                  'Crypto amount: {amount} {currency}\n'
                  'To USD: ${usd_amount}\n'
                  'Commission: ${usd_commission}\n'
                  'USD rate: ${usd_rate}\n'),
                now=datetime.datetime.now(),
                amount=deposit_info['amount'],
                currency=deposit_info['currency'].verbose_telegram,
                usd_amount=deposit_info['usd_amount'],
                usd_commission=deposit_info['usd_commission'],
                usd_rate=deposit_info['usd_rate'],
            ),
            reply_markup=markup,
        )

    @transaction.atomic()
    def make_deposit_message(self, user: BaseUserData):
        deposit_info = self.storage.pop(user.chat_id)
        deposit = create_deposit_by_telegram(user.obj, deposit_info)

        markup = keyboards.get_deposit_keyboard(deposit.pk)

        return dict(
            text=make_text(_('Your deposit: {pk}'),
                           pk=deposit.pk,),
            reply_markup=markup,
        )

    def call(self, message: types.Message, user: BaseUserData, extra: dict) -> dict:
        if extra['cb_data'] == 'deposit' or len(message.text.split()) == 1:
            markup = keyboards.get_create_deposit_keyboard()
            if extra['cb_data']:
                markup.row(get_back_button(pattern='orders'))

            return dict(
                text=make_text(_('Do you want create order?\n\n...manual text...')),
                reply_markup=markup,
            )
        elif extra['cb_data'].startswith('deposit:cancel:'):
            cancel_deposit(user.obj, pk=int(extra['cb_data'].replace('deposit:cancel:', '')))
            return dict(
                text=make_text('CANCEL! ' + message.text)
            )

        if not self.storage.get(user.chat_id):
            return dict(
                text=make_text(_('Not found')),
            )

        cb_data = callbacks.deposit_answer.parse(extra['cb_data'])
        match cb_data['answer']:
            case callbacks.Answer.NO:
                del self.storage[user.chat_id]
                return dict(
                    text=make_text(_('Deposit cancelled'))
                )
            case callbacks.Answer.YES:
                return self.make_deposit_message(user)

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
                text=make_text(_('Choose currency')),
                reply_markup=markup,
            )
        elif extra['cb_data'].startswith('deposit:currency:'):
            self.storage[user.chat_id] = {
                'currency': Currency.objects.get(
                    pk=int(extra['cb_data'].replace('deposit:currency:', ''))
                ),
            }
            return dict(
                text=make_text(_('Write amount:')),
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
                amount = self.storage[user.chat_id]['currency'].str_to_decimal(message.text)
            except decimal.InvalidOperation:
                return dict(
                    text=make_text(_('Invalid amount'))
                )

            self.storage[user.chat_id].update({
                'amount': amount,
            })
            return self.make_answer_message(user)
