from aiogram import Bot, Dispatcher

import settings

app = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(app)
