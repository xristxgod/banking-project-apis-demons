from telebot import types

EMPTY_REF_CODE = 'empty'


def get_referral_code(message: types.Message) -> str:
    arr = message.text.split()
    if len(arr) == 2:
        return arr[1]
    return EMPTY_REF_CODE
