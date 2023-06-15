from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

import settings
from apps import wallets, telegram

app = FastAPI()

app.include_router(wallets.router, prefix='/wallet')
app.include_router(telegram.router, prefix='/telegram-bot')


@app.on_event('startup')
async def startup():
    register_tortoise(
        app=app,
        db_url=settings.DATABASE_URL,
        modules={'models': settings.APPS_MODELS},
        generate_schemas=True,
        add_exception_handlers=True,
    )
