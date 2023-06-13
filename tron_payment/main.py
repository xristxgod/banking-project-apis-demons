from fastapi import FastAPI

from apps import router

app = FastAPI()
app.include_router(router)
