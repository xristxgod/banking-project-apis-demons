from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

from apps.cryptocurrencies.models import Currency
from apps.telegram.bot_apps.orders.storage import DepositStorage
from apps.telegram.bot_apps.base.keyboards import get_back_button
from apps.telegram.bot_apps.start.handlers import StartHandler
from apps.telegram.bot_apps.utils import make_text
from apps.telegram.bot_apps.middlewares import BaseUserData
from apps.telegram.bot_apps.orders import keyboards


deposit_storage = DepositStorage()


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

    def call(self, message: types.Message, user: BaseUserData, cb_data: str) -> dict:
        markup = keyboards.get_orders_keyboard()
        if cb_data:
            markup.row(get_back_button(pattern='menu'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:\n\n'
                             'Quick deposit creation:\n'
                             '`/makedeposit <network>:<currency> <amount>`')),
            reply_markup=markup,
        )


class PreMakeDepositHandlers(StartHandler):
    reg_text_pattern = r'^[A-z]+:[A-z]+ \d*[.,]?\d+$'

    use_text_params = True

    def registration_handlers(self):
        self.bot.register_message_handler(
            callback=self,
            commands=['makedeposit'],
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'make_deposit',
        )

    @staticmethod
    def get_correct_params(text_params: str) -> tuple:
        currency, amount = text_params.split()
        network_name, currency_symbol = currency.split(':')
        return network_name, currency_symbol, amount

    @classmethod
    def make_response(cls, deposit_info: dict, user: BaseUserData) -> dict:
        return dict(
            text=make_text(_('You want to deposit:\n\n'
                             'Amount: {amount} {currency}'),
                           currency=deposit_info['currency'],
                           amount=deposit_info['amount']),
            reply_markup=keyboards.get_pre_make_deposit_keyboard(),
        )

    def call_with_text_params(self, message: types.Message, user: BaseUserData, text_params: str) -> dict:
        # TODO add if has deposit
        network_name, currency_symbol, amount = self.get_correct_params(text_params)

        qs = Currency.objects.filter(
            network__name__iexact=network_name,
            symbol__iexact=currency_symbol,
        )

        if not qs.exists():
            return dict(
                text=make_text(_('Currency: `{currency}` not found!'),
                               currency=f'{network_name}:{currency_symbol}')
            )

        currency = qs.first()

        deposit_info = deposit_storage.create(
            chat_id=user.chat_id,
            params=dict(
                currency=currency,
                amount=currency.str_to_decimal(amount),
            )
        )

        return self.make_response(deposit_info=deposit_info, user=user)

    def call(self, message: types.Message, user: BaseUserData, cb_data: str) -> dict:
        if not cb_data:
            return {}
