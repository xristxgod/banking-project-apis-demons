from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from apps.telegram import messanger
from apps.telegram.models import User
from apps.telegram.bot_apps.start.utils import get_app_texts
from apps.telegram.bot_apps.start import keyboards


async def start(message: types.Message, state: FSMContext, user: User):
    if state:
        await state.finish()

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
