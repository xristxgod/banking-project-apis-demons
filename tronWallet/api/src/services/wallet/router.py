from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .services.mainTRX import trx_wallet
from .services.tokenTRC10 import trc10_tokens
from .services.tokenTRC20 import trc20_tokens

from .schemas import (
    BodyCreateWallet, ResponseCreateWallet,
    ResponseGetBalance, BodyAddNewTokenTRC20, ResponseAddNewTokenTRC20,
    BodyUnfreezeBalance, ResponseGetAllTokens, BodyFreezeBalance,
)

from api.src.config import logger
from api.src.utils.tron_typing import TronAccountAddress, TokenTRC10
from api.src.services.transaction.schemas import ResponseCreateTransaction

router = APIRouter(
)

@router.post(
    "/create-wallet",
    response_model=ResponseCreateWallet,
    description="This method creates a tron wallet",
    tags=["Wallet TRX"]
)
async def create_wallet(body: BodyCreateWallet):
    try:
        logger.error(f"Calling '/create-wallet'")
        return trx_wallet.create_wallet(body=body)
    except Exception as error:
        return {"error": str(error)}

# <<<----------------------------------->>> Wallet info <<<---------------------------------------------------------->>>

@router.get(
    "/get-account-resource/{address}",
    description="Get resource info of an account",
    response_class=JSONResponse,
    tags=["Wallet Information"]
)
async def get_account_resource(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/get-account-resource'")
        return JSONResponse(content=trx_wallet.get_account_resource(address=address))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.get(
    "/get-unspent-bandwidth/{address}",
    description="Get the unspent bandwidth",
    response_class=JSONResponse,
    tags=["Wallet Information"]
)
async def get_unspent_bandwidth(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/get-unspent-bandwidth'")
        return JSONResponse(content=trx_wallet.get_unspent_bandwidth_by_address(address=address))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.get(
    "/get-unspent-energy/{address}",
    description="Get the unspent energy",
    response_class=JSONResponse,
    tags=["Wallet Information"]
)
async def get_unspent_energy(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/get-unspent-energy'")
        return JSONResponse(content=trx_wallet.get_unspent_energy_by_address(address=address))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<------------------------------------>>> Token info <<<---------------------------------------------------------->>>

@router.get(
    "/get-all-tokens",
    description="Get all tokens",
    response_model=ResponseGetAllTokens,
    tags=["Token"]
)
async def get_all_tokens():
    try:
        logger.error(f"Calling '/get-all-tokens'")
        return trx_wallet.get_all_tokens()
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> TRX <<<------------------------------------------------------------------>>>

@router.get(
    "/get-balance/{address}",
    description="Show TRX balance on wallet address",
    response_model=ResponseGetBalance,
    tags=["Wallet TRX"]
)
async def get_trx_balance(address: TronAccountAddress):
    try:
        logger.error(f"Calling '/get-balance/{address}'")
        return trx_wallet.get_balance(address=address)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> TRC10 <<<---------------------------------------------------------------->>>

@router.get(
    "/get-trc10-balance/{address}/{token}",
    description="Show TRC10 balance on wallet address",
    response_model=ResponseGetBalance,
    tags=["Token TRC10"]
)
async def get_trc10_balance(address: TronAccountAddress, token=TokenTRC10):
    try:
        logger.error(f"Calling '/get-trc10-balance/{address}/{token}'")
        return trc10_tokens.get_balance(address=address, token=token)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> TRC20 <<<---------------------------------------------------------------->>>

@router.get(
    "/get-trc20-balance/{address}/{token}",
    description="Show TRC20 balance on wallet address",
    response_model=ResponseGetBalance,
    tags=["Token TRC20"]
)
async def get_trc20_balance(address: TronAccountAddress, token=TokenTRC10):
    try:
        logger.error(f"Calling '/get-trc20-balance/{address}/{token}'")
        return trc20_tokens.get_balance(address=address, token=token)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.post(
    "/add-trc20-token",
    description="Add a new TRC20 token",
    response_model=ResponseAddNewTokenTRC20,
    tags=["Token"]
)
async def add_new_trc20_token(body: BodyAddNewTokenTRC20):
    try:
        logger.error(f"Calling '/add-trc20-token'")
        return trc20_tokens.add_new_token(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> Freeze and Unfreeze account <<<----------------------------------------->>>

@router.post(
    "/create-freeze-balance",
    description="Create a freeze balance",
    response_model=ResponseCreateTransaction,
    tags=["Freeze and Unfreeze"]
)
async def create_freeze_balance(body: BodyFreezeBalance):
    try:
        logger.error(f"Calling '/create-freeze-balance'")
        return trx_wallet.create_freeze_balance(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.post(
    "/create-unfreeze-balance",
    description="Create a unfreeze balance",
    response_model=ResponseCreateTransaction,
    tags=["Freeze and Unfreeze"]
)
async def create_unfreeze_balance(body: BodyUnfreezeBalance):
    try:
        logger.error(f"Calling '/create-unfreeze-balance'")
        return trx_wallet.create_unfreeze_balance(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})