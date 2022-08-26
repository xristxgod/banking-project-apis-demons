import os
import uuid
import json
import decimal
from dataclasses import asdict
from typing import Optional, Union, Any, List
from decimal import Decimal, localcontext

import aiofiles

from .schemas import Header, SendTransactionData
from config import LAST_BLOCK, NOT_SEND


class Utils:
    SUN = Decimal("1000000")
    MIN_SUN = 0
    MAX_SUN = 2 ** 256 - 1

    @staticmethod
    def from_sun(num: Union[int, float]) -> Union[int, Decimal]:
        """
        Helper function that will convert a value in TRX to SUN
        :param num: Value in TRX to convert to SUN
        """
        if num == 0:
            return 0
        if num < Utils.MIN_SUN or num > Utils.MAX_SUN:
            raise ValueError("Value must be between 1 and 2**256 - 1")

        unit_value = Utils.SUN

        with localcontext() as ctx:
            ctx.prec = 999
            d_num = Decimal(value=num, context=ctx)
            result = d_num / unit_value

        return result

    @staticmethod
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
        unit_value = Utils.SUN

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

        if result < Utils.MIN_SUN or result > Utils.MAX_SUN:
            raise ValueError("Resulting wei value must be between 1 and 2**256 - 1")

        return int(result)

    @staticmethod
    def json_default(obj: Any) -> Any:
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return str(obj)


class BaseFileGet:
    @staticmethod
    async def get() -> Optional[Any]:
        raise NotImplementedError


class BaseFileSave:
    @staticmethod
    def save(**kwargs) -> Optional:
        raise NotImplementedError


class LastBlock(BaseFileGet, BaseFileSave):
    @staticmethod
    async def get() -> Optional[str]:
        """
        Get data from the file
        :return: Block number
        """
        async with aiofiles.open(LAST_BLOCK, "r") as file:
            return await file.read()

    @staticmethod
    async def save(number: int) -> Optional:
        """
        Save data to the file
        :param number: Block number
        """
        async with aiofiles.open(LAST_BLOCK, "w") as file:
            await file.write(str(number))


class NotSend(BaseFileSave):
    @staticmethod
    async def save(data: List[Header, SendTransactionData]) -> Optional:
        """"""
        new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
        async with aiofiles.open(new_not_send_file, 'w') as file:
            # Write all the verified data to a json file, and do not praise the work
            await file.write(json.dumps([asdict(data[0]), asdict(data[1])]))


__all__ = [
    "Utils", "LastBlock", "NotSend"
]