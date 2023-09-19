import abc
from typing import Type

from core.common.dao import BaseDAO


class JSONModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, f'field__{key}', value)

    def to_json(self):
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('field__'):
                result.update({
                    key.replace('field__', ''): value,
                })
        return result


class AbstractModelService(metaclass=abc.ABCMeta):
    dao: Type[BaseDAO] = NotADirectoryError

    @abc.abstractclassmethod
    async def create(cls, models: list[JSONModel], **kwargs): ...
