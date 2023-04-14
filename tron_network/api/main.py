from fastapi import FastAPI

from app import router
from config import Config


app = FastAPI(
    title=f"TronNetwork '{Config.NETWORK}'",
    description="Service for interacting with the Tron network.",
    version="1.0.0",
)
app.include_router(router=router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app")
