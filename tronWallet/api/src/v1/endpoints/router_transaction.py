from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.v1.transaction import get_transaction, get_all_transactions
from src.v1.schemas import ResponseCreateTransaction, BodyCreateTransaction, BodySignAndSendTransaction
from src.v1.services.create_transaction import create_transaction as crt
from src.v1.services.sign_send_transaction import sign_send_transaction
from src.utils.types import TronAccountAddress, TransactionHash, Coins
from config import logger

router = APIRouter()

# <<<----------------------------------->>> Fee <<<------------------------------------------------------------------>>>

@router.get(
    "/tron/get-optimal-fee/{fromAddress}&{toAddress}", description="Get a fixed transaction fee USDT",
    response_class=JSONResponse, tags=["Transaction TRX"]
)
async def get_trx_fee(fromAddress: TronAccountAddress, toAddress: TronAccountAddress):
    try:
        logger.error(f"Calling '/tron/get-fee/{fromAddress}&{toAddress}'")
        return JSONResponse(content=crt.get_optimal_fee(from_address=fromAddress, to_address=toAddress))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.get(
    "/tron_trc20_{coin}/get-optimal-fee/{fromAddress}&{toAddress}", description="Get a fixed transaction fee USDT",
    response_class=JSONResponse, tags=["Transaction Tokens"]
)
async def get_trc20_fee(fromAddress: TronAccountAddress, toAddress: TronAccountAddress, coin: str):
    try:
        logger.error(f"Calling '/tron-trc20-{coin}/get-fee/{fromAddress}&{toAddress}'")
        if Coins.is_native(coin=coin):
            return JSONResponse(content=crt.get_optimal_fee(from_address=fromAddress, to_address=toAddress))
        elif Coins.is_token(coin=coin):
            return JSONResponse(content=crt.get_optimal_fee(
                from_address=fromAddress, to_address=toAddress, token=coin
            ))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> Transactions info <<<---------------------------------------------------->>>

@router.get(
    "/tron/get-transaction/{trxHash}", description="Get transaction by transaction hash",
    response_class=JSONResponse, tags=["Transaction Information"]
)
async def get_transaction_by_tx_id(trxHash: TransactionHash):
    try:
        logger.error(f"Calling '/tron/get-transaction/{trxHash}'")
        return JSONResponse(content=get_transaction(transaction_hash=trxHash).result())
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.get(
    "/tron/get-all-transactions/{address}", description="Get transaction by transaction hash",
    response_class=JSONResponse, tags=["Transaction Information"]
)
async def get_all_transactions_by_address(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/tron/get-all-transactions/{address}'")
        return JSONResponse(content=get_all_transactions(address).result())
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> Create transaction <<<--------------------------------------------------->>>

@router.post(
    "/tron/create-transaction-for-internal-services", response_model=ResponseCreateTransaction,
    tags=["Transaction TRX"], description="Create transaction with sending from any address to any another",
)
async def create_transaction(body: BodyCreateTransaction):
    try:
        logger.error(f"Calling '/tron/create-transaction'")
        return crt.create_transaction(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})


@router.post(
    "/tron_trc20_{coin}/create-transaction-for-internal-services", response_model=ResponseCreateTransaction,
    tags=["Transaction Tokens"], description="Create transaction with sending from any address to any another",
)
async def create_trc20_transaction(body: BodyCreateTransaction, coin: str):
    try:
        logger.error(f"Calling '/tron-trc20-{coin}/create-transaction'")
        if Coins.is_native(coin=coin):
            return crt.create_transaction(body=body)
        elif Coins.is_token(coin=coin):
            return crt.create_trc20_transactions(body=body, token=coin)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> Sing and Send transactions <<<------------------------------------------->>>

@router.post(
    "/tron/sign-send-transaction-for-internal-services", description="Sign and Send a transaction",
    response_class=JSONResponse, tags=["Transaction TRX"]
)
def sign_and_send_transaction(body: BodySignAndSendTransaction):
    try:
        logger.error(f"Calling '/tron/sign-send-transaction-for-internal-services'")
        return JSONResponse(content=sign_send_transaction.sign_and_send_transaction(body=body))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.post(
    "/tron_trc20_{coin}/sign-send-transaction-for-internal-services", description="Sign and Send a transaction",
    response_class=JSONResponse, tags=["Transaction Tokens"]
)
def sign_and_send_transaction(body: BodySignAndSendTransaction, coin: str):
    try:
        logger.error(f"Calling '/tron-trc20-{coin}/sign-send-transaction-for-internal-services'")
        return JSONResponse(content=sign_send_transaction.sign_and_send_transaction(body=body))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})