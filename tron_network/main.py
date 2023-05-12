from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from tronpy.exceptions import AddressNotFound

from core import database
from core.crypto import node
from apps import router

app = FastAPI()

database.connect_fastapi(app)

app.include_router(router, prefix='/api')


@app.on_event('startup')
async def startup():
    await node.update_contracts()


@app.exception_handler(AddressNotFound)
async def unicorn_exception_handler(request: Request, exc: AddressNotFound):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": f"From address not found",
        },
    )
