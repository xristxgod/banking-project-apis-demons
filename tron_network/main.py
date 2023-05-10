from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from tronpy.exceptions import AddressNotFound

from apps import router

app = FastAPI()

app.include_router(router)


@app.exception_handler(AddressNotFound)
async def unicorn_exception_handler(request: Request, exc: AddressNotFound):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": f"From address not found",
        },
    )
