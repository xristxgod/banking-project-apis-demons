from src.services.inc.send_transaction import create_transaction, sign_send_transaction
from src.utils.types import TronAccountAddress
from config import AdminAddress, AdminPrivateKey, logger, decimals

async def activate_account(from_address: TronAccountAddress) -> bool:
    try:
        amount = decimals.create_decimal("0.1")
        logger.error(f"Create transfer: {AdminAddress} -> {from_address} for activate account | Amount: {amount}")
        txn = await create_transaction(from_address=AdminAddress, to_address=from_address, amount=amount)
        logger.error(f"Sign and Send: {AdminAddress} -> {from_address} | Amount: {amount}")
        await sign_send_transaction(createTxHex=txn["createTxHex"], private_key=AdminPrivateKey, )
        return True
    except Exception as error:
        logger.error(f"{error}")
        return False