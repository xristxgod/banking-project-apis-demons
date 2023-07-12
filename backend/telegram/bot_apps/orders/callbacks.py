import enum

from telebot.callback_data import CallbackData

deposit = CallbackData('type', prefix='deposit')
withdraw = CallbackData('type', prefix='withdraw')
repeat_deposit = CallbackData('pk', prefix='repeat_deposit')


class PaymentType:
    ACTIVE = 'active'
    LAST = 'last'
    HISTORY = 'history'


class Answer:
    YES = 'yes'
    NO = 'no'
