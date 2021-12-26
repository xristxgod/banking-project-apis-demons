from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

import src
from src.config import logger

from src.services.wallet.schemas import (
    BodyCreateWallet, BodyAddNewTokenTRC20,
    BodyFreezeBalance, BodyUnfreezeBalance,
)
from src.services.transaction.schemas import (
    BodyCreateTransaction, BodySignAndSendTransaction
)

app = FastAPI(
    title="TronNetwork",
    description="Service for interacting with the Tron network.",
    version="1.0.0"
)

app.include_router(src.router)

@app.get(
    "/docs-json",
    description="Documentation in json",
    response_class=JSONResponse,
    tags=["Documentation in json format"]
)
def documentation_json():
    logger.error(f"Calling '/docs-json'")
    return JSONResponse({
        # TRX
        "create_wallet": ["POST", "/create-wallet", BodyCreateWallet.schema()],
        "get_balance": ["GET", "/get-balance/{address}"],
        # TRC10 token
        "get_trc10_balance": ["GET", "/get-trc10-balance/{address}/{token}"],
        # TRC20 token
        "get_trc20_balance": ["GET", "/get-trc20-balance/{address}/{token}"],
        "add_trc20_token": ["POST", "/add-trc20-token", BodyAddNewTokenTRC20.schema()],
        # Freeze and Unfreeze
        "create_freeze_balance": ["POST", "/create-freeze-balance", BodyFreezeBalance.schema()],
        "create_unfreeze_balance": ["POST", "/create-unfreeze-balance", BodyUnfreezeBalance.schema()],
        # Transaction TRX
        "create_transaction_trx": ["POST", "/create-transaction", BodyCreateTransaction.schema()],
        # Transaction TRC10 token
        "create_transaction_trc10": ["POST", "/create-trc10-transaction", BodyCreateTransaction.schema()],
        # Transaction TRC20 token
        "create_transaction_trc20": ["POST", "/create-trc20-transaction", BodyCreateTransaction.schema()],
        # Sign and send transaction
        "sign_send_transaction": ["POST", "/sign-send-transaction", BodySignAndSendTransaction.schema()],
        # Transaction info
        "get_transaction": ["GET", "/get-transaction/{trxHash}"],
        "get_all_transactions": ["GET", "/get-all-transactions/{address}"],
        # Account info
        "get_account_resource": ["GET", "/get-account-resource/{address}"],
        "get_unspent_bandwidth": ["GET", "/get-unspent-bandwidth/{address}"],
        "get_unspent_energy": ["GET", "/get-unspent-energy/{address}"],
        # Transaction info
        "get_total_received": ["GET", "/get-received/{address}"],
        "get_total_send": ["GET", "/get-send/{address}"],
        "get_total_fee": ["GET", "/get-fee-spent/{address}"],
        # Fee info
        "get_fee_limit_trc20": ["GET", "/get-trc20-fee/{token}"],
        "get_fee_limit_trx_trc10": ["GET", "/get-fee/{address}"]
    })

if __name__ == '__main__':
    # Run app
    uvicorn.run("api.app:app")
