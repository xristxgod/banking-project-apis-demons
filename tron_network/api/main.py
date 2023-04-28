from fastapi import FastAPI

from src import exceptions
from src.routers import router

app = FastAPI()

app.include_router(router)


@app.exception_handler(exceptions.CurrencyNotFound)
async def currency_not_found_exception_handler(request, exc):
    pass


@app.on_event('startup')
async def startup():
    from src.settings import settings
    await settings.setup()


@app.on_event('event каждый 5 часов')
async def update_node():
    from src.core import controller
    await controller.update()
