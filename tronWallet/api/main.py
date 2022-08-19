from fastapi import FastAPI

from config import Config


app = FastAPI(
    title=f"TronNetwork '{Config.NETWORK}'",
    description="Service for interacting with the Tron network.",
    version="1.0.0",
)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app")
