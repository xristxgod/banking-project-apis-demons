import base58
from typing import Union
from datetime import datetime
from decimal import Decimal, localcontext

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