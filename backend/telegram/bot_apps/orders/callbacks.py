import enum

from telebot.callback_data import CallbackData

empty = ''

deposit = CallbackData('type', prefix='deposit')
withdraw = CallbackData('type', prefix='withdraw')

create_deposit = CallbackData('step', 'data', prefix='create-deposit')
repeat_deposit = CallbackData('pk', prefix='repeat-deposit')


class CreateDepositStep:
    START = 0
    CURRENCY = 1
    TYPE = 2
    AMOUNT = 3
    QUESTION = 4


class PaymentType:
    ACTIVE = 'active'
    LAST = 'last'
    HISTORY = 'history'


class Answer:
    YES = 'yes'
    NO = 'no'
