import re
import decimal

from telebot import types
from telebot.callback_data import CallbackData
from django.utils.translation import gettext as _

from apps.cryptocurrencies.services import get_currency
from apps.orders.services import calculate_deposit_amount

from telegram.utils import make_text
from telegram.middlewares.request import Request
from telegram.bot_apps.start.handlers import StartHandler
from telegram.bot_apps.base.keyboards import get_back_button, get_back_keyboard

from telegram.bot_apps.orders import utils
from telegram.bot_apps.orders import keyboards
from telegram.bot_apps.orders import callbacks


class OrderHandler(StartHandler):
    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            regexp=r'^/order[s]?$'
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data == 'orders',
        )

    def call(self, request: Request) -> dict:
        markup = keyboards.get_orders_keyboard(request)
        if request.data:
            markup.row(get_back_button('menu'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=markup,
        )


class BaseViewPaymentHandler(StartHandler):
    regexp: str
    callback: CallbackData

    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            regexp=self.regexp
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=self.callback.filter(),
        )

    def get_request_type(self, request: Request) -> str:
        if request.has_text_params:
            return request.text_params
        else:
            return self.callback.parse(request.data)['type']

    def call(self, request: Request) -> dict:
        match self.get_request_type(request):
            case callbacks.PaymentType.ACTIVE:
                return self.view_active(request)
            case callbacks.PaymentType.LAST:
                return self.view_last(request)
            case callbacks.PaymentType.HISTORY:
                return self.view_history(request)

    def not_found(self, request: Request) -> dict: ...

    def view_active(self, request: Request) -> dict: ...

    def view_last(self, request: Request) -> dict: ...

    def view_history(self, request: Request) -> dict: ...


class ViewDepositHandler(BaseViewPaymentHandler):
    regexp = r'^/deposit[ ]?((active)|(last)|(history))?$'
    callback = callbacks.deposit

    def view_active(self, request: Request) -> dict:
        if obj := request.user.active_deposit:
            return utils.view_active_deposit(obj)
        return utils.not_found_deposit(request)

    def view_last(self, request: Request) -> dict:
        if obj := request.user.last_deposit:
            return utils.view_last_deposit(obj)
        return utils.not_found_deposit(request)

    def view_history(self, request: Request) -> dict:
        # TODO
        pass


class ViewWithdrawHandler(BaseViewPaymentHandler):
    regexp = r'^/withdraw[ ]?((active)|(last)|(history))?$'
    callback = callbacks.withdraw

    def view_active(self, request: Request) -> dict:
        if obj := request.user.active_withdraw:
            return utils.view_active_withdraw(obj)
        return utils.not_found_withdraw(request)

    def view_last(self, request: Request) -> dict:
        if obj := request.user.last_withdraw:
            return utils.view_last_withdraw(obj)
        return utils.not_found_withdraw(request)

    def view_history(self, request: Request) -> dict:
        # TODO
        pass


class CreateDepositHandler(StartHandler):
    close_text = (
        'exit', '/exit',
    )

    def attach(self):
        self.bot.register_callback_query_handler(
            callback=self,
            func=lambda call: call.data.startswith('create-deposit'),
        )

    def create_deposit(self, request: Request, prefix: str) -> dict:
        if not self.storage.has(chat_id=request.user.id):
            raise ValueError()

        usdt_info = calculate_deposit_amount(
            request.user,
            amount=self.storage[request.user.id]['amount'],
            currency=self.storage[request.user.id]['currency'],
        )
        self.storage.update(
            chat_id=request.user.id,
            **usdt_info,
        )

        return utils.view_create_deposit_question(
            payment_info=self.storage[request.user.id],
            prefix=prefix,
        )

    def call(self, request: Request) -> dict:
        if request.data.startswith('create-deposit:step#0'):
            self.storage.delete(request.user.id)
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(
                    text=make_text(_('Create')),
                    callback_data='create-deposit:step#1'
                ),
                get_back_button('orders'),
            )
            return dict(
                text=make_text(_(
                    'Do you make deposit'
                )),
                reply_markup=markup,
            )
        elif request.data.startswith('create-deposit:step#1'):
            self.storage[request.user.id] = {
                'currency': None,
                'amount': None,
                'usdt_exchange_rate': None,
                'usdt_amount': None,
                'usdt_commission': None,
            }
            markup = keyboards.get_currencies_keyboard('create-deposit:step#2')
            return dict(
                text=make_text(_(
                    'Take currency'
                )),
                reply_markup=markup,
            )
        elif request.data.startswith('create-deposit:step#2'):
            currency_id = int(request.data.replace('create-deposit:step#2:', ''))
            self.storage.update(
                request.user.id,
                set_step=True,
                currency=get_currency(currency_id),
            )
            request.data = 'create-deposit:step#3'
            return dict(
                text=make_text(_(
                    'Write amount',
                )),
            )
        elif request.data.startswith('create-deposit:step#3'):
            if request.text in self.close_text:
                self.storage.delete(request.user.id)
                return dict(
                    text=_('Ok'),
                    reply_markup=get_back_keyboard('orders'),
                )

            if re.match(r'^\d{1,25}([,.]\d{1,18})?$', request.text) is None:
                return dict(
                    text=make_text(_(
                        'Write amount',
                    )),
                )
            self.storage.update(
                chat_id=request.user.id,
                set_step=False,
                amount=decimal.Decimal(request.text, context=decimal.Context(prec=999)),
            )
            return self.create_deposit(
                request,
                prefix='create-deposit:step#4',
            )
        elif request.data.startswith('create-deposit:step#4'):
            pass
