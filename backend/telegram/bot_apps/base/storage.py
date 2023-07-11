from typing import Optional, Callable

buffer = {}


class MemoryStorage:
    storage = buffer

    def __init__(self, _class: object):
        self.key = (_class.__module__, _class.__class__.__name__)
        if not self.storage.get(self.key):
            self.storage[self.key] = {}

    def __getitem__(self, chat_id: int):
        return self.storage[self.key][chat_id]

    def __setitem__(self, chat_id: int, value: dict):
        if value.get('step') and value.get('data'):
            self.storage[self.key][chat_id] = value
        else:
            self.storage[self.key][chat_id] = {
                'step': {
                    'callback': None,
                    'set': False,
                },
                'data': value,
            }

    def has(self, chat_id: int) -> bool:
        return self.get(chat_id) is not None

    def get(self, chat_id: int) -> Optional[dict]:
        return self.storage[self.key].get(chat_id)

    def delete(self, chat_id: int):
        if self.has(chat_id):
            del self.storage[self.key][chat_id]

    def update(self, chat_id: int, *, set_step: bool = None, callback: Callable = None, **params):
        pass