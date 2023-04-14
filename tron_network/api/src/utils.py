import decimal
import functools
from typing import Type, Callable, Optional


def exception_handler(cls_exc: list[Type[Exception]] | Type[Exception],
                      return_cls_exc: Optional[Type[Exception]] = None):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except cls_exc as err:
                cls = return_cls_exc or Exception
                raise cls(err)
        return wrapper
    return decorator


def from_sun(amount: decimal.Decimal) -> decimal.Decimal:
    if amount > 2**256 - 1:
        raise ValueError("Value must be between 1 and 2**256 - 1")

    with decimal.localcontext() as ctx:
        ctx.prec = 999
        d_num = decimal.Decimal(value=amount, context=ctx)
        result = d_num / decimal.Decimal("1000000")

    return result


def to_sun(amount: decimal.Decimal) -> int:
    str_amount = str(amount)
    unit_value = decimal.Decimal("1000000")

    if amount < 1 and "." in str_amount:
        with decimal.localcontext() as ctx:
            multiplier = len(str_amount) - str_amount.index(".") - 1
            ctx.prec = multiplier
            amount = decimal.Decimal(value=amount, context=ctx) * 10 ** multiplier
        unit_value /= 10 ** multiplier

    with decimal.localcontext() as ctx:
        ctx.prec = 999
        result = decimal.Decimal(value=amount, context=ctx) * unit_value

    if result < 0 or result > 2**256 - 1:
        raise ValueError("Resulting wei value must be between 1 and 2**256 - 1")

    return int(result)
