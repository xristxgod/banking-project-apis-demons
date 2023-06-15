from fastapi import APIRouter
from fastapi.requests import Request

from aiogram import Dispatcher, Bot, types

import settings
from apps.telegram.bot import app, dp

router = APIRouter()


# @router.on_event('startup')
# async def startup():
#     webhook_info = await app.get_webhook_info()
#     if webhook_info.url != settings.TELEGRAM_WEBHOOK_URL:
#         await app.set_webhook(
#             url=settings.TELEGRAM_WEBHOOK_URL
#         )
#
#
# @router.on_event("shutdown")
# async def shutdown():
#     await app.session.close()


@router.post('/webhook')
async def bot_webhook(request: Request):
    telegram_update = types.Update(**await request.json())
    Dispatcher.set_current(dp)
    Bot.set_current(app)
    await dp.process_update(telegram_update)
