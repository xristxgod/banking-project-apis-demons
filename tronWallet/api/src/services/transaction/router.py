from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .services.mainTRX import transaction_trx
from .services.tokenTRC10 import transaction_trc10
from .services.tokenTRC20 import transaction_trc20
from .schemas import (
    BodyCreateTransaction, ResponseCreateTransaction, ResponseGetFeeLimit,
    BodySignAndSendTransaction, ResponseTransactions
)

from api.src.config import logger
from api.src.utils.tron_typing import TransactionHash, TronAccountAddress, TokenTRC20

router = APIRouter()

# <<<----------------------------------->>>Fee info<<<--------------------------------------------------------------->>>

@router.get(
    "/get-trc20-fee/{token}",
    description="Find out what will be the commission for the TRC20 transaction",
    response_model=ResponseGetFeeLimit,
    tags=["Fee Information"]
)
async def get_fee_limit_trc20(token: TokenTRC20):
    try:
        logger.error(f"Calling '/get-trc20-fee/{token}'")
        return transaction_trc20.get_fee_limit(token=token)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.get(
    "/get-fee/{address}",
    description="Find out what will be the commission for TRX and TRC10 transactions",
    response_model=ResponseGetFeeLimit,
    tags=["Fee Information"]
)
async def get_fee_limit_trx_trc10(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/get-fee/{address}'")
        return transaction_trx.get_fee_limit(from_address=address)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>>Transactions info<<<------------------------------------------------------>>>

@router.get(
    "/get-transaction/{trxHash}",
    description="Get transaction by transaction hash",
    response_class=JSONResponse,
    tags=["Transactions Information"]
)
async def get_transaction(trxHash: TransactionHash):
    try:
        logger.error(f"Calling '/get-transaction/{trxHash}'")
        return JSONResponse(content=transaction_trx.get_transaction(trxHash=trxHash))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.get(
    "/get-all-transactions/{address}",
    description="Get transaction by transaction hash",
    response_class=JSONResponse,
    tags=["Transactions Information"]
)
async def get_all_transactions(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/get-all-transactions/{address}'")
        return JSONResponse(content=transaction_trx.get_all_transactions(address=address))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>>Account info<<<----------------------------------------------------------->>>

@router.get(
    "/get-received/{address}",
    description="Get total received",
    response_class=JSONResponse,
    tags=["Wallet Information"]
)
async def get_total_received(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/get-received/{address}'")
        total_received = transaction_trx.get_received_or_send_or_fee(address=address)["totalReceived"]
        return JSONResponse(content={"totalReceived": str(total_received)})
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.get(
    "/get-send/{address}",
    description="Get total send",
    response_class=JSONResponse,
    tags=["Wallet Information"]
)
async def get_total_send(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/get-send/{address}'")
        total_send = transaction_trx.get_received_or_send_or_fee(address=address)["totalSend"]
        return JSONResponse(content={"totalSend": str(total_send)})
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.get(
    "/get-fee-spent/{address}",
    description="Collect the spent commission",
    response_class=JSONResponse,
    tags=["Wallet Information"]
)
async def get_fee_spent(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/get-fee-spent/{address}'")
        total_fee = transaction_trx.get_received_or_send_or_fee(address=address)["totalFee"]
        return JSONResponse(content={"totalFee": str(total_fee)})
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>>TRX<<<-------------------------------------------------------------------->>>

@router.post(
    "/create-transaction",
    description="Create a TRX transaction",
    response_model=ResponseCreateTransaction,
    tags=["Wallet TRX"]
)
async def create_trx_transactions(body: BodyCreateTransaction):
    try:
        logger.error(f"Calling '/create-transaction'")
        return transaction_trx.create_transaction(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>>TRC10<<<------------------------------------------------------------------>>>

@router.post(
    "/create-trc10-transaction",
    description="Create a TRC10 transaction",
    response_model=ResponseCreateTransaction,
    tags=["Token TRC10"]
)
async def create_trc10_transactions(body: BodyCreateTransaction):
    try:
        logger.error(f"Calling '/create-trc10-transaction'")
        return transaction_trc10.create_transaction(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>>TRC20<<<------------------------------------------------------------------>>>

@router.post(
    "/create-trc20-transaction",
    description="Create a TRC20 transaction",
    response_model=ResponseCreateTransaction,
tags=["Token TRC20"]
)
async def create_trc20_transactions(body: BodyCreateTransaction):
    try:
        logger.error(f"Calling '/create-trc20-transaction'")
        return transaction_trc20.create_transaction(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<-------------------->>>Sing and Send transactions (TRX, TRC10, TRC20, Freeze, Unfreeze)<<<---------------------->>>

@router.post(
    "/sign-send-transaction",
    description="Sign and Send a transaction",
    response_model=ResponseTransactions,
    tags=["Token TRC10", "Token TRC20", "Freeze and Unfreeze"]
)
def sign_and_send_transaction(body: BodySignAndSendTransaction):
    try:
        logger.error(f"Calling '/sign-send-transaction'")
        return transaction_trx.sign_send_transaction(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})