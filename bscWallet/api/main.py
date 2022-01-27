from fastapi import FastAPI

from config import logger
from src.v1.services.wallet_eth import wallet_bsc

from src.v1.routers import router_v2


app = FastAPI(
    title=f"Binance Smart Chain",
    description="Service for interacting with the BSC network.",
    version="1.0.0",
)


app.include_router(router_v2)


@app.get("/", tags=['Utils'])
async def is_connected():
    """Check connection status"""
    logger.error(f"Calling '/is-connected'")
    status = await wallet_bsc.node_bridge.is_connect()
    if status:
        return {"message": "Connection established"}
    return {"message": "No connection"}


@app.get("/get-gas-price", tags=['Utils'])
async def get_gas_price():
    gas_price = await wallet_bsc.node_bridge.gas_price
    if gas_price:
        logger.error(f"Calling '/get-gas-price' | {gas_price}")
        return {"gasPrice": str(gas_price)}
    return {"message": "No connection"}


@app.get("/docs-json", tags=['Utils'])
async def index():
    logger.error(f"Calling '/docs'")
    return {
        "Check connection status": [
            "GET", "/"
        ],
        "create_wallet": [
            "POST", "/create-wallet", "Description: Create ethereum wallet."
        ],
        "create_deterministic_wallet": [
            "POST", "/create-deterministic-wallet", "Description: Create deterministic ethereum wallet."
        ],
        "get_balance": [
            "GET", "/bsc/get-balance", "Description: Returns ethereum balance."
        ],
        "get_token_balance": [
            "GET", "/{token}/get-balance", "Description: Returns the balance of the token(contract)."
        ],
        "add_token": [
            "POST", "/add-new-token", "Description: Add a new token(contract) if it is not in the system."
        ],
        "get_all_tokens": [
            "GET", "/get-all-files", "Description: Will return all files(contracts)."
        ],

        "create_transaction": [
            "POST", "/bsc/sign-transaction", "Description: Will create unsigned ethereum transaction"
        ],
        "sign_send_transaction": [
            "POST", "/bsc/sign-send-transaction", "Description: Sign and send ethereum transaction"
        ],

        "create_token_transaction": [
            "POST", "/{token}/create-transaction",
            "Description: Will create a token transaction"
        ],
        "sign_send_token_transaction": [
            "POST", "/{token}/sign-send-transaction", "Description: Sign and send token transaction"
        ],

        "get_transaction": [
            "GET", "/get-transaction", "Description: Returns information about the transaction"
        ],
        "get_optimal_gas": [
            "GET", "/get-optimal-gas", "Description: Returns optimal gas"
        ],
        "get_gas_price": [
            "GET", "/get-gas-price", "Description: Will return the gas price"
        ]
    }
