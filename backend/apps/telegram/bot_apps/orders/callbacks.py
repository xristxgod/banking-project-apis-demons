import enum

from telebot.callback_data import CallbackData

deposit_answer = CallbackData('answer', prefix='deposit_answer')


class Answer(enum.StrEnum):
    NO = 'no'
    YES = 'yes'
