from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src_v1.v1.wallet import wallet
from src_v1.v1.schemas import ResponseCreateWallet, BodyCreateWallet, ResponseGetBalance
from src_v1.utils.types import TronAccountAddress, Coins
from config import logger


router = APIRouter()


# <<<------------------------------------>>> Wallet <<<-------------------------------------------------------------->>>


@router.post(
    "/{network}/create-wallet", response_model=ResponseCreateWallet,
    description="This method creates a tron wallet", tags=["Wallet"]
)
async def create_wallet(body: BodyCreateWallet, network: Optional[str] = "tron"):
    try:
        logger.error(f"Calling 'v1/{network}/create-wallet'")
        return wallet.create_wallet(body=body)
    except Exception as error:
        return {"error": str(error)}


# <<<------------------------------------>>> Balance <<<------------------------------------------------------------->>>


@router.get(
    "/tron/get-balance/{address}", description="Show only TRC20 USDT balance on wallet address",
    response_model=ResponseGetBalance, tags=["Wallet"]
)
async def get_balance(address: TronAccountAddress):
    try:
        logger.error(f"Calling 'tron/get-balance/{address}'")
        return await wallet.get_balance(address=address)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})


@router.get(
    "/tron_trc20_{coin}/get-balance/{address}", description="Show only TRC20 USDT balance on wallet address",
    response_model=ResponseGetBalance, tags=["Wallet"]
)
async def get_trc20_balance(address: TronAccountAddress, coin: str):
    try:
        logger.error(f"Calling 'tron-trc20-{coin}/get-balance/{address}'")
        if Coins.is_native(coin=coin):
            return await wallet.get_balance(address=address)
        elif Coins.is_token(coin=coin):
            return await wallet.get_token_balance(address=address, token=coin)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    except Exception as error:
        return JSONResponse(content={"error": str(error)})
