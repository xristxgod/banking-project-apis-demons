from telebot.callback_data import CallbackData
from django.utils.translation import gettext as _

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
