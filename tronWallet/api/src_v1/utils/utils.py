from decimal import Decimal, localcontext
from typing import Union

import requests
from tronpy.tron import Tron, HTTPProvider

from config import network, NGINX_DOMAIN


TIMERS = 10
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


# <<<----------------------------------->>> Project status utils <<<------------------------------------------------->>>


def is_block_ex(our_block: int, public_block: int, accept: int = 20) -> bool:
    """Check if the block is not lagging behind."""
    if (our_block == public_block) or (public_block - our_block <= accept):
        return True
    else:
        return False


def get_public_node() -> Tron:
    """Returns a working public node"""
    for public_node in ["http://3.225.171.164:8090", "http://52.53.189.99:8090", "http://18.196.99.16:8090"]:
        try:
            __node = Tron(
                provider=HTTPProvider(public_node),
                network="mainnet")
            if int(__node.get_node_info()["activeConnectCount"]) == 0:
                raise Exception
            else:
                return __node
        except Exception as error:
            continue
    else:
        raise Exception("Public node is bad")


def get_last_block() -> int:
    """Get the last block from the file"""
    return int(requests.request("GET", f"{NGINX_DOMAIN}/get-last-block-file").text)
