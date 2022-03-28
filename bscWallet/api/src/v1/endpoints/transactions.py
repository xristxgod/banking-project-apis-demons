from fastapi import APIRouter, HTTPException, status

from config import ADMIN_PRIVATE_KEY
from src.utils.es_send import send_msg_to_kibana
from src.v1.schemas import BodyCreateTransaction, ResponseCreateTransaction, BodySendTransaction, \
    ResponseSendTransaction, BodyGetTx, BodyGetOptimalGas
from src.v1.services.trx_eth import transaction_bsc
from src.v1.services.trx_tokens import transaction_token
from src.v1.types import Coins


transactions_router = APIRouter(tags=['Transactions'])


@transactions_router.post(
    "/bnb/create-transaction",
    description="Create a BSC transaction for sending ONLY from ADMIN_ADDRESS",
    response_model=ResponseCreateTransaction,
)
async def create_transactions_bnb(body: BodyCreateTransaction):
    return await __create_transaction(coin='bnb', body=body)


@transactions_router.post(
    "/bsc_bip20_{coin}/create-transaction",
    description="Create a BSC transaction for sending ONLY from ADMIN_ADDRESS",
    response_model=ResponseCreateTransaction,
)
async def create_transactions(coin: str, body: BodyCreateTransaction):
    return await __create_transaction(coin=coin, body=body)


async def __create_transaction(coin: str, body: BodyCreateTransaction):
    try:
        if Coins.is_native(coin):
            return await transaction_bsc.create_transaction(body=body, is_admin=True)
        elif Coins.is_token(coin):
            return await transaction_token.create_transaction(body=body, token=coin, is_admin=True)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    except Exception as error:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'{error}'
        )


@transactions_router.post(
    "/bsc_bip20_{coin}/create-transaction-for-internal-services",
    description="Create a BSC transaction with sending from any address to any another",
    response_model=ResponseCreateTransaction,
)
async def create_transactions(coin: str, body: BodyCreateTransaction):
    try:
        if Coins.is_native(coin):
            return await transaction_bsc.create_transaction(body=body)
        elif Coins.is_token(coin):
            return await transaction_token.create_transaction(body=body, token=coin)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    except Exception as error:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'{error}'
        )


@transactions_router.post(
    "/bnb/sign-send-transaction",
    description="Sign and send a BSC transaction",
    response_model=ResponseSendTransaction,
)
async def send_transaction_bnb(body: BodySendTransaction):
    return await __send_transaction(coin='bnb', body=body)


@transactions_router.post(
    "/bsc_bip20_{coin}/sign-send-transaction",
    description="Sign and send a BSC transaction",
    response_model=ResponseSendTransaction,
)
async def send_transaction(coin: str, body: BodySendTransaction):
    return await __send_transaction(coin=coin, body=body)


async def __send_transaction(coin: str, body: BodySendTransaction):
    """Create, sign and send token transaction"""
    body.privateKeys = [ADMIN_PRIVATE_KEY]
    if Coins.is_native(coin):
        tx = await transaction_bsc.sign_send_transaction(body=body, is_sender_from_body=True)
    elif Coins.is_token(coin):
        tx = await transaction_token.sign_send_transaction(body=body, is_sender_from_body=True)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    await send_msg_to_kibana(msg=f'SENDED TX: {tx.json()}')
    return tx


@transactions_router.post(
    "/bsc_bip20_{coin}/sign-send-transaction-for-internal-services",
    description="Sign and send a BSC transaction with sending from any address to any another",
    response_model=ResponseSendTransaction,
)
async def send_transaction(coin: str, body: BodySendTransaction):
    """Create, sign and send token transaction"""
    if Coins.is_native(coin):
        return await transaction_bsc.sign_send_transaction(body=body)
    elif Coins.is_token(coin):
        return await transaction_token.sign_send_transaction(body=body)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')


@transactions_router.post(
    "/bsc/get-transaction",
    description="Get a BSC transaction",
)
async def get_transaction(body: BodyGetTx):
    """Get transaction"""
    return await transaction_bsc.get_transaction(
        transaction_hash=body.trxHash
    )


@transactions_router.post(
    "/bsc_bip20_{coin}/get-optimal-gas",
    description="optimal gas value for BSC transaction",
)
async def get_optimal_gas(coin: str, body: BodyGetOptimalGas):
    """Get optimal gas for transaction"""
    if Coins.is_native(coin):
        return await transaction_bsc.get_optimal_gas(
            from_address=body.fromAddress,
            to_address=body.toAddress,
            amount=body.amount
        )
    elif Coins.is_token(coin):
        return await transaction_token.get_optimal_gas(
            from_address=body.fromAddress,
            to_address=body.toAddress,
            amount=body.amount,
            token=coin
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
