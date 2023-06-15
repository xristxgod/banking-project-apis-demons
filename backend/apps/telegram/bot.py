from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import settings
from apps.telegram.bot_apps import init_all_handlers

app = Bot(token=settings.TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(app, storage=storage)

# Init bot apps
init_all_handlers(dp)
