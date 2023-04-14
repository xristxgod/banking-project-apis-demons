from fastapi import FastAPI

from src import exceptions

app = FastAPI()


@app.exception_handler(exceptions.CurrencyNotFound)
async def currency_not_found_exception_handler(request, exc):
    pass


@app.on_event('startup')
async def startup():
    from src.settings import settings
    await settings.setup()


@app.on_event()
async def update_node():
    from src.core import controller
    await controller.update()
