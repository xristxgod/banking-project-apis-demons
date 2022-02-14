from decimal import Decimal, localcontext
from typing import Union
from datetime import datetime

SUN = Decimal("1000000")
MIN_SUN = 0
MAX_SUN = 2**256 - 1

# <<<----------------------------------->>> Convert TRX to SUN to TRX <<<-------------------------------------------->>>

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

def to_sun(num: Union[int, float]) -> int:
    """
    Helper function that will convert a value in TRX to SUN
    :param num: Value in TRX to convert to SUN
    """
    if isinstance(num, int) or isinstance(num, str):
        d_num = Decimal(value=num)
    elif isinstance(num, float):
        d_num = Decimal(value=str(num))
    elif isinstance(num, Decimal):
        d_num = num
    else:
        raise TypeError("Unsupported type. Must be one of integer, float, or string")

    s_num = str(num)
    unit_value = SUN

    if d_num == 0:
        return 0

    if d_num < 1 and "." in s_num:
        with localcontext() as ctx:
            multiplier = len(s_num) - s_num.index(".") - 1
            ctx.prec = multiplier
            d_num = Decimal(value=num, context=ctx) * 10 ** multiplier
        unit_value /= 10 ** multiplier

    with localcontext() as ctx:
        ctx.prec = 999
        result = Decimal(value=d_num, context=ctx) * unit_value

    if result < MIN_SUN or result > MAX_SUN:
        raise ValueError("Resulting wei value must be between 1 and 2**256 - 1")

    return int(result)

# <<<----------------------------------->>> Convert time to datetime <<<--------------------------------------------->>>

def convert_time(t: str) -> str:
    return datetime.fromtimestamp(int(str(t)[:10])).strftime('%d-%m-%Y %H:%M:%S')