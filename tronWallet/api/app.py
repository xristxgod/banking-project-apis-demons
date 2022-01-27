from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.v1.schemas import BodyCreateWallet, BodyCreateTransaction, BodySignAndSendTransaction
from src import router
from config import logger, network

app = FastAPI(
    title=f"TronNetwork '{network}'",
    description="Service for interacting with the Tron network.",
    version="1.0.0",
    docs_url="/tron/docs",
    redoc_url="/tron/redoc"
)

app.include_router(router)

@app.get(
    "/tron/docs-json", description="Documentation in json",
    response_class=JSONResponse, tags=["Utils"]
)
async def documentation_json():
    logger.error(f"Calling '/docs-json'")
    return JSONResponse({
        # Wallet
        "create_wallet": ["POST", "/{network}/create-wallet", BodyCreateWallet.schema()],
        "get_balance": ["GET", "/tron-trc20-{coin}/get-balance/{address}"],
        # Transaction
        "create_transaction": ["POST", "/tron-trc20-{coin}/create-transaction-for-internal-services", BodyCreateTransaction.schema()],
        "sign_send_transaction": ["POST", "/tron-trc20-{coin}/sign-send-transaction-for-internal-services", BodySignAndSendTransaction.schema()],
        # Transaction Admin
        "create_admin_transaction": ["POST", "/tron-trc20-{coin}/create-transaction", BodyCreateTransaction.schema()],
        "sign_send_admin_transaction": ["POST", "/tron-trc20-{coin}/sign-send-transaction", BodySignAndSendTransaction.schema()],
        # Transaction info
        "get_transaction": ["GET", "/tron/get-transaction/{trxHash}"],
        "get_all_transactions": ["GET", "/tron/get-all-transactions/{address}"],
        # Fee
        "get_optimal_fee": ["GET", "/tron-trc20-{coin}/get-optimal-fee/{fromAddress}&{toAddress}"],
        # Utils
        "get_all_tokens": ["GET", "/tron/get-all-tokens/"],
        "docs": ["GET", "/tron/docs/ or /tron/redoc/"]
    })

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app")