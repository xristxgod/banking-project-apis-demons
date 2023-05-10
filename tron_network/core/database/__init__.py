from typing import Optional, NoReturn

import fastapi
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

import settings


def connect_fastapi(
        app: fastapi.FastAPI,
        config: dict = settings.DATABASE_CONFIG,
) -> NoReturn:
    register_tortoise(
        app=app,
        config=config,
        generate_schemas=True,
        add_exception_handlers=True,
    )


async def connect(config: dict = settings.DATABASE_CONFIG):
    await Tortoise.init(config=config)


async def drop():
    await Tortoise._drop_databases()
