import enum

from telebot.callback_data import CallbackData

deposit_answer = CallbackData('answer', prefix='deposit_answer')
deposit_step = CallbackData('step', prefix='deposit_step')


class DepositAnswer(enum.StrEnum):
    NO = 'no'
    YES = 'yes'


class DepositStep(enum.StrEnum):
    CHOOSE_CURRENCY = 'choose_currency'
