from src_1.services.inc.send_transaction import create_transaction, sign_send_transaction
from src_1.utils.es_send import send_msg_to_kibana, send_exception_to_kibana
from src_1.utils.types import TronAccountAddress
from config import AdminAddress, AdminPrivateKey, logger, decimals


async def activate_account(from_address: TronAccountAddress) -> bool:
    try:
        amount = decimals.create_decimal("0.00001")
        logger.error(f"Create transfer: {AdminAddress} -> {from_address} for activate account | Amount: {amount}")
        await send_msg_to_kibana(msg=f"Create transfer: {AdminAddress} -> {from_address} for activate account | Amount: {amount}")
        txn = await create_transaction(from_address=AdminAddress, to_address=from_address, amount=amount)
        logger.error(f"Sign and Send: {AdminAddress} -> {from_address} for activate account | Amount: {amount}")
        await send_msg_to_kibana(msg=f"Sign and Send: {AdminAddress} -> {from_address} for activate account | Amount: {amount}")
        await sign_send_transaction(createTxHex=txn["createTxHex"], private_key=AdminPrivateKey, )
        return True
    except Exception as error:
        logger.error(f"{error}")
        await send_exception_to_kibana(error, "ERROR: ACTIVATE ACCOUNT")
        return False
