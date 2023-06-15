from aiogram import types

from apps.telegram.utils import Text
from apps.telegram.models import Language


# TODO add callback data
async def get_registration_keyboard(obj: Text):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.InlineKeyboardButton(
            text=await obj.get('registration_button'),
            callback_data='',
        )
    )
    return keyboard


# TODO add callback data
async def get_menu_keyboard(obj: Text, lang: Language):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Choose language
    keyboard.add(
        types.InlineKeyboardButton(
            text=await obj.get('choose_lang_button', lang=lang),
            callback_data=''
        )
    )

    # Show balance
    keyboard.add(
        types.InlineKeyboardButton(
            text=await obj.get('show_balance_button', lang=lang),
            callback_data='',
        )
    )

    # Deposit
    keyboard.add(
        types.InlineKeyboardButton(
            text=await obj.get('deposit_button', lang=lang),
            callback_data='',
        )
    )

    return keyboard
