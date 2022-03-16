from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.v1.transaction import transaction_parser
from src.v1.schemas import ResponseCreateTransaction, BodyCreateTransaction, BodySignAndSendTransaction
from src.v1.services.create_transaction import create_transaction as crt
from src.v1.services.sign_send_transaction import sign_and_send_transaction as send
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
        result = await crt.get_optimal_fee(from_address=fromAddress, to_address=toAddress)
        return JSONResponse(content=result)
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
            result = await crt.get_optimal_fee(from_address=fromAddress, to_address=toAddress)
            return JSONResponse(content=result)
        elif Coins.is_token(coin=coin):
            result = await crt.get_optimal_fee(from_address=fromAddress, to_address=toAddress, token=coin)
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> Transactions info <<<---------------------------------------------------->>>

@router.get(
    "/{network}/get-transaction/{trxHash}", description="Get transaction by transaction hash",
    response_class=JSONResponse, tags=["Transaction Information"]
)
async def get_transaction_by_tx_id(trxHash: TransactionHash, network: str):
    try:
        logger.error(f"Calling '/tron/get-transaction/{trxHash}'")
        result = await transaction_parser.get_transaction(transaction_hash=trxHash)
        return JSONResponse(content=result)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.get(
    "/{network}/get-all-transactions/{address}", description="Get transaction by transaction hash",
    response_class=JSONResponse, tags=["Transaction Information"]
)
async def get_all_transactions_by_address(address: TronAccountAddress, network: str):
    try:
        logger.error(f"Calling '/{network}/get-all-transactions/{address}'")
        if network.lower() in ["tron_trc20_usdt", "tron_trc20_usdc", "tron_trc20_trx", "trx", "tron"]:
            result = await transaction_parser.get_all_transactions(
                address=address, token=network[11:15] if network not in ["trx", "tron", "tron_trc20_trx"] else None
            )
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Network "{network}" was not found')
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> Create transaction <<<--------------------------------------------------->>>

@router.post(
    "/tron/create-transaction-for-internal-services", response_model=ResponseCreateTransaction,
    tags=["Transaction TRX"], description="Create transaction with sending from any address to any another",
)
async def create_transaction(body: BodyCreateTransaction):
    try:
        body.adminFee = 0
        logger.error(f"Calling '/tron/create-transaction'")
        return await crt.create_transaction(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})


@router.post(
    "/tron_trc20_{coin}/create-transaction-for-internal-services", response_model=ResponseCreateTransaction,
    tags=["Transaction Tokens"], description="Create transaction with sending from any address to any another",
)
async def create_trc20_transaction(body: BodyCreateTransaction, coin: str):
    try:
        logger.error(f"Calling '/tron-trc20-{coin}/create-transaction'")
        body.adminFee = 0
        if Coins.is_native(coin=coin):
            return await crt.create_transaction(body=body)
        elif Coins.is_token(coin=coin):
            return await crt.create_trc20_transactions(body=body, token=coin)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> Sing and Send transactions <<<------------------------------------------->>>

@router.post(
    "/{network}/sign-send-transaction-for-internal-services", description="Sign and Send a transaction",
    response_class=JSONResponse, tags=["Transaction TRX", "Transaction Tokens"]
)
async def sign_and_send_transaction(body: BodySignAndSendTransaction, network: str):
    try:
        logger.error(f"Calling '/{network}/sign-send-transaction-for-internal-services'")
        result = await send(body=body)
        return JSONResponse(content=result)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})