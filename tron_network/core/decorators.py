import asyncio
import functools
from typing import Callable, Optional

from cryptography.fernet import Fernet

import settings

fernet = Fernet(settings.CODER_SECRET_KEY)


def decode(*, values: Optional[list] = None, type=object, take: str = 'request'):
    """
    This function decodes the response or result

    :param values: what needs to be decoded
    :param type: object or dict
    :param take: request or response
    """
    use_this: bool = settings.USE_CODER

    def decode_func(value: str) -> str:
        return fernet.decrypt(value.encode()).decode()

    def decode_request(**kwargs):
        for k, v in kwargs.items():
            if type == str:
                kwargs[k] = decode_func(v)
                continue

            for value in values:
                if type == object:
                    setattr(v, value, decode_func(getattr(v, value)))
                elif type == dict:
                    v[value] = decode_func(v[value])
            kwargs[k] = v
        return kwargs

    def decode_response(response: object | dict):
        if isinstance(response, str):
            return decode_func(response)

        for value in values:
            if type == object:
                setattr(response, value, decode_func(getattr(response, value)))
            elif type == dict:
                response[value] = decode_func(response[value])
        return response

    def decorator(func: Callable):
        async def async_wrapper(**kwargs):
            response = await func(**kwargs)
            if use_this and take == 'response':
                response = decode_response(response)
            return response

        def wrapper(**kwargs):
            response = func(**kwargs)
            if use_this and take == 'response':
                response = decode_response(response)
            return response

        @functools.wraps(func)
        def controller(**kwargs):
            if use_this and take == 'request':
                kwargs = decode_request(**kwargs)

            if asyncio.iscoroutinefunction(func):
                return async_wrapper(**kwargs)
            else:
                return wrapper(**kwargs)
        return controller

    return decorator


def encode(*, values: Optional[list] = None, type=object, take: str = 'request'):
    """
    This function encodes the response or result

    :param values: what needs to be encoded
    :param type: object or dict or str
    :param take: request or response
    """
    use_this: bool = settings.USE_CODER

    def encode_func(value: str) -> str:
        return fernet.encrypt(value.encode()).decode()

    def encode_request(**kwargs):
        for k, v in kwargs.items():
            if type == str:
                kwargs[k] = encode_func(v)
                continue

            for value in values:
                if type == object:
                    setattr(v, value, encode_func(getattr(v, value)))
                elif type == dict:
                    v[value] = encode_func(v[value])
            kwargs[k] = v
        return kwargs

    def encode_response(response: object | dict):
        if isinstance(response, str):
            return encode_func(response)

        for value in values:
            if type == object:
                setattr(response, value, encode_func(getattr(response, value)))
            elif type == dict:
                response[value] = encode_func(response[value])
        return response

    def decorator(func: Callable):
        async def async_wrapper(**kwargs):
            response = await func(**kwargs)
            if use_this and take == 'response':
                response = encode_response(response)
            return response

        def wrapper(**kwargs):
            response = func(**kwargs)
            if use_this and take == 'response':
                response = encode_response(response)
            return response

        @functools.wraps(func)
        def controller(**kwargs):
            if use_this and take == 'request':
                kwargs = encode_request(**kwargs)

            if asyncio.iscoroutinefunction(func):
                return async_wrapper(**kwargs)
            else:
                return wrapper(**kwargs)
        return controller

    return decorator
