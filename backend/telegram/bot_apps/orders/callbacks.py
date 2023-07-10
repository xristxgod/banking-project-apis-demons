import enum

from telebot.callback_data import CallbackData

deposit = CallbackData('type', prefix='deposit')
withdraw = CallbackData('type', prefix='withdraw')
repeat_deposit = CallbackData('pk', prefix='repeat_deposit')
make_deposit_question = CallbackData('answer', prefix='make_deposit_question')


class PaymentType:
    ACTIVE = 'active'
    LAST = 'last'
    HISTORY = 'history'


class MakeDepositQuestion(enum.StrEnum):
    YES = 'yes'
    NO = 'no'
