from fastapi import APIRouter, HTTPException, status
from src.v1.schemas import BodyAddressOnly, BodyCreateWallet
from src.v1.services.wallet_eth import wallet_bsc
from src.v1.services.wallet_tokens import wallet_tokens
from src.v1.types import Coins


wallet_router = APIRouter(tags=['Wallet'])


@wallet_router.post("/{network}/create-wallet")
async def create_wallet(network: str, body: BodyCreateWallet):
    """ This method creates an ether wallet """
    return await wallet_bsc.create_wallet(body.words)


@wallet_router.post("/bsc_bip20_{coin}/get-balance")
async def get_balance(coin: str, body: BodyAddressOnly):
    """ Show Ether balance at wallet address """
    if Coins.is_native(coin):
        return await wallet_bsc.get_balance(address=body.address)
    elif Coins.is_token(coin):
        return await wallet_tokens.get_balance(address=body.address, symbol=coin)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
