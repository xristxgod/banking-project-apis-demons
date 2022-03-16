from decimal import Decimal

from src.services.inc.send_transaction import create_transaction, sign_send_transaction
from src.utils.es_send import send_msg_to_kibana, send_exception_to_kibana
from src.utils.types import TronAccountAddress
from config import AdminAddress, AdminPrivateKey, logger

async def get_trx_for_fee(to_address: TronAccountAddress, fee: Decimal) -> bool:
    try:
        logger.error(f"Create transfer: {AdminAddress} -> {to_address} | Amount: {fee}")
        await send_msg_to_kibana(msg=f"Create transfer: {AdminAddress} -> {to_address} | Amount: {fee}")
        txn = await create_transaction(from_address=AdminAddress, to_address=to_address, amount=fee)
        logger.error(f"Sign and Send: {AdminAddress} -> {to_address} | Amount: {fee}")
        await send_msg_to_kibana(msg=f"Sign and Send: {AdminAddress} -> {to_address} | Amount: {fee}")
        return await sign_send_transaction(createTxHex=txn["createTxHex"], private_key=AdminPrivateKey)
    except Exception as error:
        logger.error(f"{error}")
        await send_exception_to_kibana(error=error, msg="ERROR: GET TRX FOR FEE")
        return False