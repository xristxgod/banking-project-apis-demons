from fastapi import FastAPI

app = FastAPI()


@app.on_event('startup')
async def startup():
    from src.settings import settings
    await settings.setup()


@app.on_event()
async def update_node():
    from src.core import controller
    await controller.update()
