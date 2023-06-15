from typing import Optional

from aiogram import types

from apps.telegram.bot import app as bot


async def send_message(chat_id: int, text: str, keyboard: Optional[types.KeyboardButton] = None):
    return await bot.send_message(
        chat_id,
        text=text,
        reply_markup=keyboard,
    )


async def edit_message(message: types.Message, text: str, keyboard: Optional[types.KeyboardButton] = None):
    return await message.edit_text(
        text=text,
        reply_markup=keyboard,
    )
