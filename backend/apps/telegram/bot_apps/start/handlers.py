from aiogram import types
from tortoise import transactions

from apps.telegram import messanger
from apps.telegram.models import User, Language
from apps.telegram.bot_apps.start.utils import get_app_texts
from apps.telegram.bot_apps.start import keyboards


async def start(message: types.Message, user: User):
    obj = await get_app_texts()

    if not user:
        text = await obj.get(pk='menu', lang=user.language)
        keyboard = keyboards.get_menu_keyboard(obj, lang=user.language)
    else:
        text = await obj.get(pk='registration')
        keyboard = await keyboards.get_registration_keyboard(obj=obj)

    await messanger.send_message(
        message.chat.id,
        text=text,
        keyboard=keyboard,
    )


@transactions.atomic()
async def registration(query: types.CallbackQuery, callback_data: dict):
    obj = await get_app_texts()

    user = User(
        id=query.message.chat.id,
        username=query.message.chat.username,
        language=await Language.default(),
    )
    await user.save()

    await messanger.edit_message(
        message=query.message,
        text=await obj.get(pk='success_registration'),
    )
