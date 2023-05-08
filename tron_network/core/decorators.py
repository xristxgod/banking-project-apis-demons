import asyncio
import functools
from typing import Callable

import settings


def decode(*, values: list, type: str = object, take: str = 'request'):
    """
    This function decodes the response or result

    :param values: what needs to be decoded
    :param type: object or dict
    :param take: request or response
    """
    use_this: bool = settings.USE_CODER

    def decode_func(value: str) -> str:
        # TODO realize this
        return value

    def decode_request(**kwargs):
        for value in values:
            kwargs[value] = decode_func(kwargs.pop(value))
        return kwargs

    def decode_response(response: object | dict):
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


def encode(*, values: list, type=object, take: str = 'request'):
    """
    This function encodes the response or result

    :param values: what needs to be encoded
    :param type: object or dict
    :param take: request or response
    """
    use_this: bool = settings.USE_CODER

    def encode_func(value: str) -> str:
        # TODO realize this
        return value

    def encode_request(**kwargs):
        for value in values:
            kwargs[value] = encode_func(kwargs.pop(value))
        return kwargs

    def encode_response(response: object | dict):
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
