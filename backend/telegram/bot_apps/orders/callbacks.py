import enum

from telebot.callback_data import CallbackData

repeat_deposit = CallbackData('pk', prefix='repeat_deposit')
make_deposit_question = CallbackData('answer', prefix='make_deposit_question')


class MakeDepositQuestion(enum.StrEnum):
    YES = 'yes'
    NO = 'no'
