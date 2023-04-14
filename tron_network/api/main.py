from fastapi import FastAPI

app = FastAPI()


@app.on_event('startup')
async def startup():
    from src.settings import settings
    await settings.setup()
