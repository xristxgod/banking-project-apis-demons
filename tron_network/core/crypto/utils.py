import decimal

UNIT_VALUE = decimal.Decimal("1000000")
MIN_SUN = 0
MAX_SUN = 2**256 - 1


def from_sun(amount: int) -> decimal.Decimal:
    if amount == 0:
        return 0
    if amount < MIN_SUN or amount > MAX_SUN:
        raise ValueError("Value must be between 1 and 2**256 - 1")

    with decimal.localcontext() as ctx:
        ctx.prec = 999
        d_num = decimal.Decimal(value=amount, context=ctx)
        result = d_num / UNIT_VALUE

    return result


def to_sun(amount: decimal.Decimal) -> int:
    if amount <= 0:
        return 0

    str_amount = str(amount)
    unit_value = UNIT_VALUE

    if amount < 1 and "." in str_amount:
        with decimal.localcontext() as ctx:
            multiplier = len(str_amount) - str_amount.index(".") - 1
            ctx.prec = multiplier
            amount = decimal.Decimal(value=amount, context=ctx) * 10 ** multiplier
        unit_value /= 10 ** multiplier

    with decimal.localcontext() as ctx:
        ctx.prec = 999
        result = decimal.Decimal(value=amount, context=ctx) * unit_value

    if result < MIN_SUN or result > MAX_SUN:
        raise ValueError("Resulting wei value must be between 1 and 2**256 - 1")

    return int(result)


def is_native(currency: str) -> bool:
    return currency.upper() == 'TRX'
