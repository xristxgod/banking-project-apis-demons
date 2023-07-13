import re
import decimal

from telebot.callback_data import CallbackData
from django.utils.translation import gettext as _

from apps.cryptocurrencies.services import get_currency
from apps.orders.services import calculate_deposit_amount

from telegram.utils import make_text
from telegram.middlewares.request import Request
from telegram.bot_apps.start.handlers import StartHandler
from telegram.bot_apps.base.keyboards import get_back_button, get_back_keyboard

from telegram.bot_apps.orders import utils
from telegram.bot_apps.orders import services
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
        markup = keyboards.get_orders_keyboard()
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
            cq_filter=callbacks.view_payment.filter(),
        )
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=self.callback.filter(),
        )

    def get_request_type(self, request: Request) -> str:
        if request.has_text_params:
            return request.text_params
        elif request.data:
            return self.callback.parse(request.data)['type']

    def call(self, request: Request) -> dict:
        if request.data.startswith('view-payment'):
            return self.view(request)

        match self.get_request_type(request):
            case callbacks.PaymentType.ACTIVE:
                return self.view_active(request)
            case callbacks.PaymentType.LAST:
                return self.view_last(request)
            case callbacks.PaymentType.HISTORY:
                return self.view_history(request)
            case _:
                return self.menu(request)

    def view(self, request: Request) -> dict:
        from apps.orders.models import Payment
        cb_data = callbacks.view_payment.parse(callback_data=request.data)

        payment = Payment.objects.filter(
            pk=int(cb_data['pk']),
            order__user=request.user,
        ).first()
        if not payment:
            return self.not_found(request)

        if payment.type in Payment.DEPOSIT_TYPES:
            result = utils.view_deposit(payment)
        else:
            result = utils.view_withdraw(payment)

        if cb_data['back'] != callbacks.empty:
            result['reply_markup'].row(get_back_button(
                self.callback.new(type=cb_data['back']),
            ))

        return result

    def menu(self, request: Request) -> dict: ...

    def not_found(self, request: Request) -> dict: ...

    def view_active(self, request: Request) -> dict: ...

    def view_last(self, request: Request) -> dict: ...

    def view_history(self, request: Request) -> dict: ...


class ViewDepositHandler(BaseViewPaymentHandler):
    regexp = r'^/deposit[ ]?((active)|(last)|(history))?$'
    callback = callbacks.deposit

    def menu(self, request: Request) -> dict:
        markup = keyboards.get_deposit_menu_keyboard(request)
        if request.data:
            markup.row(get_back_button('orders'))

        return dict(
            text=make_text(_(':upwards_button: Select actions: :downwards_button:')),
            reply_markup=markup,
        )

    def not_found(self, request: Request) -> dict:
        return utils.not_found_deposit()

    def view_active(self, request: Request) -> dict:
        if obj := request.user.active_deposit:
            result = utils.view_active_deposit(obj, request)
            result['reply_markup'].row(get_back_button(
                callbacks.deposit.new(type='menu')
            ))
            return result
        return self.not_found(request)

    def view_last(self, request: Request) -> dict:
        if obj := request.user.last_deposit:
            result = utils.view_last_deposit(obj)
            result['reply_markup'].row(get_back_button(
                callbacks.deposit.new(type='menu')
            ))
            return result
        return self.not_found(request)

    def view_history(self, request: Request) -> dict:
        if request.user.deposit_history(limit=5):
            result = utils.view_deposit_history(request)
            result['reply_markup'].row(get_back_button(
                callbacks.deposit.new(type='menu')
            ))
            return result
        return self.not_found(request)


class ViewWithdrawHandler(BaseViewPaymentHandler):
    regexp = r'^/withdraw[ ]?((active)|(last)|(history))?$'
    callback = callbacks.withdraw

    def not_found(self, request: Request) -> dict:
        return utils.not_found_withdraw(request)

    def view_active(self, request: Request) -> dict:
        if obj := request.user.active_withdraw:
            return utils.view_active_withdraw(obj)
        return self.not_found(request)

    def view_last(self, request: Request) -> dict:
        if obj := request.user.last_withdraw:
            return utils.view_last_withdraw(obj)
        return self.not_found(request)

    def view_history(self, request: Request) -> dict:
        # TODO
        pass


class CreateDepositHandler(StartHandler):
    storage_key = 'CreateDeposit'
    close_text = (
        'exit', '/exit',
    )

    def attach(self):
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.create_deposit.filter(),
        )

    def create_deposit(self, request: Request) -> dict:
        if not self.storage.has(chat_id=request.user.id):
            raise ValueError()

        usdt_info = calculate_deposit_amount(
            request.user,
            amount=self.storage[request.user.id]['data']['amount'],
            currency=self.storage[request.user.id]['data']['currency'],
        )
        self.storage.update(
            chat_id=request.user.id,
            usdt_exchange_rate=usdt_info['usdt_info']['price'],
            usdt_amount=usdt_info['usdt_amount'],
            usdt_commission=usdt_info['usdt_commission'],
        )

        return utils.view_create_deposit_question(
            payment_info=self.storage[request.user.id]['data'],
            callback=callbacks.create_deposit,
            extra=dict(step=callbacks.CreateDepositStep.QUESTION),
        )

    def make_deposit(self, request: Request) -> dict:
        return services.make_deposit(request, self.storage.pop(request.user.id))

    def call(self, request: Request) -> dict:
        cb_data = callbacks.create_deposit.parse(callback_data=request.data)

        if not self.storage.has(request.user.id) and int(cb_data['step']) != callbacks.CreateDepositStep.START:
            return dict(
                text=make_text(_(':no_entry:')),
            )

        match int(cb_data['step']):
            case callbacks.CreateDepositStep.START:
                self.storage[request.user.id] = {
                    'currency': None,
                    'amount': None,
                    'deposit_type': None,
                    'usdt_exchange_rate': None,
                    'usdt_amount': None,
                    'usdt_commission': None,
                }
                markup = keyboards.get_currencies_keyboard(
                    callbacks.create_deposit,
                    extra=dict(step=callbacks.CreateDepositStep.CURRENCY),
                )
                return dict(
                    text=make_text(_(
                        ':down_right_arrow: Choose a currency :down_left_arrow:'
                    )),
                    reply_markup=markup,
                )
            case callbacks.CreateDepositStep.CURRENCY:
                self.storage.update(
                    request.user.id,
                    currency=get_currency(int(cb_data['data'])),
                )
                markup = keyboards.get_deposit_type_keyboard(
                    callbacks.create_deposit,
                    extra=dict(step=callbacks.CreateDepositStep.TYPE),
                )

                return dict(
                    text=make_text(_(':down_right_arrow: Select the deposit type :down_left_arrow:')),
                    reply_markup=markup,
                )
            case callbacks.CreateDepositStep.TYPE:
                self.storage.update(
                    request.user.id,
                    set_step=True,
                    deposit_type=cb_data['data'],
                )
                request.data = callbacks.create_deposit.new(
                    step=callbacks.CreateDepositStep.AMOUNT,
                    data=callbacks.empty
                )

                return dict(
                    text=make_text(_(
                        ':down_right_arrow: Enter the amount :down_left_arrow:\n\n'
                        'Input format:\n'
                        '\t<amount>.<amount>\n'
                        '\t<amount>,<amount>\n'
                        '\t<amount>\n\n'
                        'Enter `/exit` to stop'
                    )),
                )
            case callbacks.CreateDepositStep.AMOUNT:
                if request.text in self.close_text:
                    self.storage.delete(request.user.id)
                    return dict(
                        text=_(':double_exclamation_mark: Creation stopped :double_exclamation_mark:'),
                        reply_markup=get_back_keyboard('orders'),
                    )
                if re.match(r'^\d{1,25}([,.]\d{1,18})?$', request.call.text) is None:
                    return dict(
                        text=make_text(_(
                            ':double_exclamation_mark: Invalid amount format\n'
                            'Input format:\n'
                            '\t<amount>.<amount>\n'
                            '\t<amount>,<amount>\n'
                            '\t<amount>\n\n'
                            'Enter `/exit` to stop'
                        )),
                    )
                self.storage.update(
                    chat_id=request.user.id,
                    set_step=False,
                    amount=decimal.Decimal(request.text, context=decimal.Context(prec=999)),
                )
                return self.create_deposit(request)
            case callbacks.CreateDepositStep.QUESTION:
                match cb_data['data']:
                    case callbacks.Answer.NO:
                        self.storage.delete(request.user.id)
                        return dict(
                            text=make_text(_(':hollow_red_circle: The deposit has been successfully cancelled!')),
                        )
                    case callbacks.Answer.YES:
                        return self.make_deposit(request)


class CreateDepositByTextHandler(CreateDepositHandler):
    regexp = r'^/(?P<method>cdeposit|qrcdeposit) (?P<network>[A-z]+):(?P<currency>[A-z]+) (?P<amount>\d*[.,]?\d+)$'

    def attach(self):
        self.bot.register_message_handler(
            callback=self,
            regexp=self.regexp,
        )

    def call(self, request: Request) -> dict:
        from apps.orders.models import Payment
        from apps.cryptocurrencies.models import Currency

        match = re.match(self.regexp, request.text)
        network_name, symbol = match.group('network'), match.group('currency')

        currency = Currency.objects.filter(
            symbol__iexact=symbol,
            network__name__iexact=network_name,
        ).first()

        if not currency:
            return dict(
                text=make_text(_(':double_exclamation_mark: This {currency} currency was not found!'),
                               currency=f'{network_name}:{symbol}')
            )

        typ = Payment.Type.DEPOSIT if match.group('method') == 'qrcdeposit' else Payment.Type.BY_PROVIDER_DEPOSIT

        self.storage[request.user.id] = {
            'currency': currency,
            'amount': decimal.Decimal(match.group('amount'), context=decimal.Context(prec=999)),
            'deposit_type': typ,
            'usdt_exchange_rate': None,
            'usdt_amount': None,
            'usdt_commission': None,
        }

        return self.create_deposit(request)


class RepeatDepositHandler(CreateDepositHandler):
    def attach(self):
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.repeat_deposit.filter(),
        )

    def call(self, request: Request) -> dict:
        from apps.orders.models import Payment

        cb_data = callbacks.repeat_deposit.parse(callback_data=request.data)

        payment = Payment.objects.get(pk=int(cb_data['pk']))

        self.storage[request.user.id] = {
            'currency': payment.order.currency,
            'amount': payment.order.amount,
            'deposit_type': payment.type,
            'usdt_exchange_rate': None,
            'usdt_amount': None,
            'usdt_commission': None,
        }

        return self.create_deposit(request)


class CancelPaymentHandler(StartHandler):
    def attach(self):
        self.bot.register_callback_query_handler(
            callback=self,
            func=None,
            cq_filter=callbacks.cancel_payment.filter(),
        )

    def call(self, request: Request) -> dict:
        from apps.orders.models import Payment

        cb_data = callbacks.cancel_payment.parse(callback_data=request.data)

        payment = Payment.objects.get(order__user=request.user, pk=int(cb_data['pk']))

        if payment.is_deposit:
            return services.cancel_deposit(request, payment)
