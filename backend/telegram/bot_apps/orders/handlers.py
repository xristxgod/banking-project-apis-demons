from telebot import types
from django.db import transaction
from django.utils.translation import gettext as _

from apps.orders.models import Deposit
from apps.cryptocurrencies.models import Currency
from apps.orders.services import calculate_deposit_amount, create_deposit, cancel_deposit

from telegram.utils import make_text
from telegram.bot_apps.base.keyboards import get_back_button, get_back_keyboard
from telegram.middlewares.request import TelegramRequest
from telegram.bot_apps.start.handlers import StartHandler

from telegram.bot_apps.orders import utils
from telegram.bot_apps.orders import keyboards
from telegram.bot_apps.orders import callbacks


temp_deposit_storage = {}


class OrdersHandler(StartHandler):
    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['orders', 'order'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'orders',
        )

    def call(self, request: TelegramRequest) -> dict:
        markup = keyboards.get_orders_keyboard(request)
        if request.data:
            markup.row(get_back_button('menu'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=markup,
        )


class DepositHandler(StartHandler):
    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['deposit', 'mydeposit', 'activedeposit'],
        )

        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'deposit',
        )

    def view_active_deposit(self, request: TelegramRequest):
        # TODO add save message_id for further modification
        return utils.view_active_deposit(request)

    def call(self, request: TelegramRequest) -> dict:
        if not request.user.has_active_deposit:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(
                text=make_text(_('Create')),
                callback_data='premakedeposit'
            ))

            return dict(
                text=make_text(_('You have a gntu of an active deposit')),
                reply_markup=markup,
            )

        return self.view_active_deposit(request)


class PreMakeDepositHandler(DepositHandler):
    help = '/makedeposit <network>:<currency> <amount>`'

    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            regexp=r'^/makedeposit( [A-z]+:[A-z]+ \d*[.,]?\d+)?$',
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'premakedeposit',
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.repeat_deposit.filter(),
        )

    @classmethod
    def by_text_params(cls, request: TelegramRequest) -> dict:
        if not request.valid_text_params(r'^[A-z]+:[A-z]+ \d*[.,]?\d+$'):
            return dict(
                text=make_text(_('Invalid params!'))
            )

        network_and_currency, amount = request.text_params.split()
        network_name, currency_symbol = network_and_currency.split(':')
        qs = Currency.objects.filter(
            network__name__iexact=network_name,
            symbol__iexact=currency_symbol,
        )
        if not qs.exists():
            return dict(
                text=make_text(_('Invalid currency!'))
            )

        currency = qs.first()
        amount = currency.str_to_decimal(amount)
        usd_info = calculate_deposit_amount(request.user.obj, amount=amount, currency=currency)

        temp_deposit_storage[request.user.chat_id] = {
            'currency': currency,
            'amount': amount,
            **usd_info,
        }

        return utils.view_question_deposit(temp_deposit_storage[request.user.chat_id])

    @classmethod
    def by_repeat_deposit(cls, request: TelegramRequest) -> dict:
        decoded_cb_data = callbacks.repeat_deposit.parse(callback_data=request.data)
        old_deposit = Deposit.objects.get(pk=decoded_cb_data['pk'])

        currency = old_deposit.order.currency
        amount = old_deposit.order.amount
        usd_info = calculate_deposit_amount(request.user.obj, amount=amount, currency=currency)

        temp_deposit_storage[request.user.chat_id] = {
            'currency': currency,
            'amount': amount,
            **usd_info,
        }

        return utils.view_question_deposit(temp_deposit_storage[request.user.chat_id])

    def call(self, request: TelegramRequest) -> dict:
        if request.user.has_active_deposit:
            return self.view_active_deposit(request)
        elif request.text_params:
            return self.by_text_params(request)
        elif request.data.startswith('repeat_deposit'):
            return self.by_repeat_deposit(request)
        else:
            pass


class MakeDepositHandler(DepositHandler):
    def attach(self):
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.make_deposit_question.filter(),
        )

    def call(self, request: TelegramRequest) -> dict:
        if not temp_deposit_storage.get(request.user.chat_id):
            return dict(
                text=make_text(_('Oops...')),
            )

        decoded_cb_data = callbacks.make_deposit_question.parse(callback_data=request.data)

        match decoded_cb_data['answer']:
            case callbacks.MakeDepositQuestion.NO:
                del temp_deposit_storage[request.user.chat_id]

                return dict(
                    text=make_text(_('Ok, I have removed your application')),
                    reply_markup=get_back_keyboard('orders'),
                )
            case callbacks.MakeDepositQuestion.YES:
                request.user.deposit = create_deposit(
                    request.user.obj,
                    deposit_info=temp_deposit_storage.pop(request.user.chat_id)
                )
                return self.view_active_deposit(request)


class CancelDepositHandler(DepositHandler):
    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['candeldeposit'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'cancel_deposit'
        )

    def call(self, request: TelegramRequest) -> dict:
        markup = get_back_keyboard('orders') if request.data else None

        if not request.user.has_active_deposit:
            return dict(
                text=make_text(_('The deposit was not found!')),
                reply_markup=markup,
            )

        request.user.deposit = cancel_deposit(request.user.deposit)
        return self.view_active_deposit(request)
