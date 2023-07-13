import datetime
import decimal


def decimal_to_str(value: decimal.Decimal) -> str:
    return str(value)


def correct_datetime(_datetime) -> str:
    if _datetime:
        return _datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
