from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import settings
from apps.telegram.bot_apps import init_all_handlers
from apps.telegram.middlewares import lifetime_middleware

app = Bot(token=settings.TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(app, storage=storage)

dp.middleware.setup(lifetime_middleware.UserDatabaseMiddleware())

# Init bot apps
init_all_handlers(dp)
