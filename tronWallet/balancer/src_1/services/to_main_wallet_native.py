from typing import Union

from src_1.utils.types import TronAccountAddress
from src_1.utils.es_send import send_msg_to_kibana, send_exception_to_kibana
from src_1.services.inc.get_balance import get_balance
from src_1.services.inc.get_private_key import get_private_key
from src_1.services.inc.send_transaction import sign_send_transaction, create_transaction
from src_1.services.inc.get_optimal_fee import get_optimal_fee
from src_1.utils.is_error import is_error
from config import AdminAddress, minTokenCost, logger


async def send_to_main_wallet_native(address: TronAccountAddress) -> Union[bool, None]:
    """
    Send funds from the user's wallet to the administrator's wallet. Exclusively TRX!
    :param address: Wallet address
    """
    try:
        # Get trx balance
        balance = await get_balance(address=address)
        logger.error(f"--> TRX | Address: {address} | Balance: {balance} | Preparing to empty the balance!!")
        if balance < minTokenCost:
            logger.error(f"--> TRX | Address: {address} | The translation doesn't make sense!!")
            return None
        # Get commission price for transaction
        fee = await get_optimal_fee(from_address=address, to_address=AdminAddress)
        # Amount to transfer
        amount = balance - fee
        if amount <= 0:
            logger.error(f"--> TRX | Address: {address} | The translation doesn't make sense!!")
            return None
        logger.error(f"--> TRX | Address: {address} | {address} -> {AdminAddress} | Amount: {amount} TRX | Fee: {fee}")
        # Create transaction
        txn = await create_transaction(from_address=address, to_address=AdminAddress, amount=amount)
        logger.error(f"--> TRX | Address: {address} | Private Key Search")
        # Get the private key for the account.
        private_key = await get_private_key(address=address)
        if private_key is not None:
            logger.error(f"--> TRX | Address: {address} | Signing and sending a transaction")
            # Sign and send transaction
            send = await sign_send_transaction(createTxHex=txn["createTxHex"], private_key=private_key)
            if not send:
                logger.error(f"--> TRX | Address: {address} | The transaction was not sent. Written to a file!!!")
                await is_error({"address": address, "token": "TRX"})
                return None
            balance = await get_balance(address=address)
            await send_msg_to_kibana(msg=f"TRX | Address: {address} | Balance: {balance} | The balance is empty")
            logger.error(f"--> TRX | Address: {address} | Balance: {balance} | The balance is empty!!!")
        else:
            logger.error(f"--> TRX | Address: {address} | The key to the address was not found. Written to a file!!!")
            await is_error({"address": address, "token": "TRX"})
    except Exception as error:
        logger.error(f"\n--> TRX | Error: {error}\n")
        await send_exception_to_kibana(error, msg="ERROR: SEND TO MAIN WALLET NATIVE")
        await is_error({"address": address, "token": "TRX"})
