import decimal

SUN = decimal.Decimal(1000000)
MIN_SUN = 0
MAX_SUN = 2**256 - 1


def from_sun(amount: int) -> decimal.Decimal:
    if amount == 0:
        return decimal.Decimal(0)
    if amount < MIN_SUN or amount > MAX_SUN:
        raise ValueError("Value must be between 1 and 2**256 - 1")

    with decimal.localcontext() as ctx:
        ctx.prec = 999
        d_num = decimal.Decimal(value=amount, context=ctx)
        result = d_num / SUN

    return result


def to_sun(amount: decimal.Decimal) -> int:
    if isinstance(amount, int) or isinstance(amount, str):
        d_num = decimal.Decimal(value=amount)
    elif isinstance(amount, float):
        d_num = decimal.Decimal(value=str(amount))
    elif isinstance(amount, decimal.Decimal):
        d_num = amount
    else:
        raise TypeError("Unsupported type. Must be one of integer, float, or string")

    s_num = str(amount)
    unit_value = SUN

    if d_num == 0:
        return 0

    if d_num < 1 and "." in s_num:
        with decimal.localcontext() as ctx:
            multiplier = len(s_num) - s_num.index(".") - 1
            ctx.prec = multiplier
            d_num = decimal.Decimal(value=amount, context=ctx) * 10 ** multiplier
        unit_value /= 10 ** multiplier

    with decimal.localcontext() as ctx:
        ctx.prec = 999
        result = decimal.Decimal(value=d_num, context=ctx) * unit_value

    if result < MIN_SUN or result > MAX_SUN:
        raise ValueError("Resulting wei value must be between 1 and 2**256 - 1")

    return int(result)
