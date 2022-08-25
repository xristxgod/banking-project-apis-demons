import os
import json
import uuid
import base58
from typing import Dict, Union, List
from datetime import datetime
from decimal import Decimal, localcontext

from aiofiles import open as async_open

from src_1.external_data.es_send import send_exception_to_kibana
from src_1.external_data.rabbit_mq import send_to_balancer, send_message
from src_1.external_data.database import get_transaction_hash, get_contracts
from config import (
    network, fileTokens, decimals, ReportingAddress,
    logger, NOT_SEND, ERROR, NOT_SEND_TO_TRANSACTION
)


# Public address of the Tron wallet (Base58 address) | Example: `TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb`
TronAccountAddress = str
# Address of the smart contract (tokens) (Base58 address) | Example: `THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF` - ETH Token
ContractAddress = str

SUN = Decimal("1000000")
MIN_SUN = 0
MAX_SUN = 2**256 - 1


def from_sun(num: Union[int, float]) -> Union[int, Decimal]:
    """
    Helper function that will convert a value in TRX to SUN
    :param num: Value in TRX to convert to SUN
    """
    if num == 0:
        return 0
    if num < MIN_SUN or num > MAX_SUN:
        raise ValueError("Value must be between 1 and 2**256 - 1")

    unit_value = SUN

    with localcontext() as ctx:
        ctx.prec = 999
        d_num = Decimal(value=num, context=ctx)
        result = d_num / unit_value

    return result


def convert_time(t: int) -> str:
    """
    Convert from timestamp to date and time
    :param t: Timestamp data
    """
    return datetime.fromtimestamp(int(t)).strftime('%d-%m-%Y %H:%M:%S')


def to_base58check_address(raw_addr: Union[str, bytes]) -> str:
    """Convert hex address or base58check address to base58check address(and verify it)."""
    if isinstance(raw_addr, (str,)):
        if raw_addr[0] == "T" and len(raw_addr) == 34:
            try:
                # assert checked
                base58.b58decode_check(raw_addr)
            except ValueError:
                raise Exception("bad base58check format")
            return raw_addr
        elif len(raw_addr) == 42:
            if raw_addr.startswith("0x"):  # eth address format
                return base58.b58encode_check(b"\x41" + bytes.fromhex(raw_addr[2:])).decode()
            else:
                return base58.b58encode_check(bytes.fromhex(raw_addr)).decode()
        elif raw_addr.startswith("0x") and len(raw_addr) == 44:
            return base58.b58encode_check(bytes.fromhex(raw_addr[2:])).decode()
    elif isinstance(raw_addr, (bytes, bytearray)):
        if len(raw_addr) == 21 and int(raw_addr[0]) == 0x41:
            return base58.b58encode_check(raw_addr).decode()
        if len(raw_addr) == 20:  # eth address format
            return base58.b58encode_check(b"\x41" + raw_addr).decode()
        return to_base58check_address(raw_addr.decode())
    raise Exception(repr(raw_addr))


async def get_asset_trc20(address: ContractAddress) -> Dict:
    """
    Get a full description of the token at its address.
    :param address: Token address
    """
    if network == "shasta" or network == "nile":
        async with async_open(fileTokens, "r", encoding="utf-8") as file:
            data: dict = json.loads(await file.read())
        tokens = data
    else:
        tokens = get_contracts()
    for token in tokens:
        if address in [token["name"], token["symbol"], token["address"]]:
            return token


def get_transaction_for_fee(transaction) -> Dict:
    """
    If the transaction is a fee payment
    :param transaction: The transaction itself
    """
    tx = transaction["transactions"][0]
    amount = decimals.create_decimal(tx["amount"])
    fee = decimals.create_decimal(tx["fee"]) if float(tx["fee"]) > 0 else 0
    from_amount = amount + fee
    return {
        "time": tx["time"],
        "transactionHash": tx["transactionHash"],
        "amount": "%.8f" % amount,
        "fee": "%.8f" % fee,
        "recipients": [],
        "senders": [{"address": ReportingAddress, "amount": "%.8f" % from_amount}]
    }


def get_transaction_in_db(transaction_hash: str, transaction: Dict) -> Dict:
    transaction_in_db = get_transaction_hash(transaction_hash=transaction_hash)
    if transaction_in_db is None:
        return transaction
    transaction["senders"] = transaction_in_db["from_wallets"]
    transaction["recipients"] = transaction_in_db["to_wallets"]
    return transaction


async def send_to_rabbit_mq(values: json) -> None:
    """
    Send collected data to queue
    :param values: Packaged transactions to send
    """
    try:
        send_message(values=values)
    except Exception as error:
        logger.error(f"fSend to MQ error: {error}")
        await send_exception_to_kibana(error=error, msg="ERROR: SEND TO RABBIT MQ")
        async with async_open(ERROR, "a", encoding="utf-8") as file:
            # If an error occurred on the RabbitMQ side, write about it.
            await file.write(f"Error Step 187: {values} | RabbitMQ not responding {error} \n")
        new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
        async with async_open(new_not_send_file, 'w') as file:
            # Write all the verified data to a json file, and do not praise the work
            await file.write(str(values))


async def send_to_rabbit_mq_balancer(values: json) -> None:
    """
        Send collected data to queue
        :param values: Packaged transactions to send
        """
    try:
        send_to_balancer(values=values)
    except Exception as error:
        logger.error(f"fSend to MQ Balancer error: {error}")
        await send_exception_to_kibana(error=error, msg="ERROR: SEND TO RABBIT MQ BALANCER")
        async with async_open(ERROR, "a", encoding="utf-8") as file:
            # If an error occurred on the RabbitMQ side, write about it.
            await file.write(f"Error Step 187: {values} | RabbitMQ not responding {error} \n")
        new_not_send_file = os.path.join(NOT_SEND_TO_TRANSACTION, f'{uuid.uuid4()}.json')
        async with async_open(new_not_send_file, 'w') as file:
            # Write all the verified data to a json file, and do not praise the work
            await file.write(str(values))
