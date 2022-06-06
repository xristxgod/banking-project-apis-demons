import asyncio

from src.services.inc.get_balance import get_balance
from src.services.inc.get_private_key import get_private_key
from src.services.inc.send_transaction import create_transaction, sign_send_transaction
from src.services.inc.get_optimal_fee import get_optimal_fee
from src.services.helper.get_trx_for_fee import get_trx_for_fee
from src.utils.es_send import send_msg_to_kibana, send_exception_to_kibana
from src.utils.types import TronAccountAddress, TokenTRC20
from src.utils.is_error import is_error
from src.services.to_main_wallet_native import send_to_main_wallet_native
from config import AdminAddress, get_network, tokens, logger, minTokenCost


async def send_to_main_wallet_token(address: TronAccountAddress, token: TokenTRC20):
    """
    Send funds from the user's wallet to the admin wallet. Exclusive tokens!!!
    :param address: Wallet address
    :param token: Token name or symbol
    """
    trx_tnx = False
    try:
        # Get a network from a token
        token_network = get_network(token=token.lower())
        # Get token balance
        balance_token = await get_balance(address=address, token=token_network)
        logger.error(f"--> {token.upper()} | Address: {address} | Balance: {balance_token} | Preparing to empty the balance!!")
        if balance_token < tokens[token.lower()]:
            logger.error(f"--> {token.upper()} | Address: {address} | Balance: {balance_token} | Not suitable for balance transfer!!")
            return None
        # Get commission price for transaction
        fee = await get_optimal_fee(from_address=address, to_address=AdminAddress, token_network=token_network)
        # Get trx balance
        balance_trx = await get_balance(address=address)
        if balance_trx - fee <= 0:
            logger.error(f"--> {token.upper()} | Address: {address} | There is not enough trx balance to transfer!!!")
            await send_msg_to_kibana(msg=f"{token.upper()} | Address: {address} | Not enough TRX balance to transfer. TRX transfer to pay commission")
            # Send a transaction to the address with the funds for the commission.
            fee_status = await get_trx_for_fee(to_address=address, fee=fee)
            if not fee_status:
                logger.error(f"--> {token.upper()} | Address: {address} | The transfer of funds for the commission has not been made. Written to a file!!!")
                await is_error({"address": address, "token": token})
                return None
            logger.error(f"--> {token.upper()} | Address: {address} | The funds for the transaction have been transferred!!!")
            await send_msg_to_kibana(msg=f"{token.upper()} | Address: {address} | Funds for the payment of the commission were transferred")
            await asyncio.sleep(10)
        if balance_trx - fee > minTokenCost:
            trx_tnx = True
        logger.error(f"--> {token.upper()} | Address: {address} | {address} -> {AdminAddress} | Amount: {balance_token} {token} | Fee: {fee}")
        txn = await create_transaction(
            token=token_network, from_address=address, to_address=AdminAddress, amount=balance_token
        )
        logger.error(f"--> {token.upper()} | Address: {address} | Private Key Search")
        private_key = await get_private_key(address=address)
        if private_key is not None:
            logger.error(f"--> {token.upper()} | Address: {address} | Signing and sending a transaction")
            # Sign and send transaction
            send = await sign_send_transaction(createTxHex=txn["createTxHex"], private_key=private_key)
            if not send:
                logger.error(f"--> {token.upper()} | Address: {address} | The transaction was not sent. Written to a file!!!")
                await is_error({"address": address, "token": token.upper()})
                return None
            balance_token = await get_balance(address=address, token=token_network)
            logger.error(f"--> {token.upper()} | Address: {address} | Balance: {balance_token} | The balance is empty!!!")
            await send_msg_to_kibana(msg=f"{token.upper()} | Address: {address} | Balance: {balance_token} | The balance is empty")
            if trx_tnx and send:
                await send_to_main_wallet_native(address=address)
        else:
            logger.error(f"--> {token.upper()} | Address: {address} | The key to the address was not found. Written to a file!!!")
            await is_error({"address": address, "token": token})
    except Exception as error:
        logger.error(f"Error: {error}")
        await send_exception_to_kibana(error, "ERROR: SEND TO MAIN WALLET TOKEN")
        await is_error({"address": address, "token": token})
