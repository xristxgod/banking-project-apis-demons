from typing import Optional, Callable

buffer = {}


class MemoryStorage:
    storage = buffer

    def __init__(self, key: object | str):
        if isinstance(key, str):
            self.key = key
        else:
            self.key = (key.__module__, key.__class__.__name__)

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
        self.storage[self.key][chat_id]['step']['callback'] = callback

        if set_step is not None:
            self.storage[self.key][chat_id]['step']['set'] = set_step

        for key, value in self.storage[self.key][chat_id]['data'].items():
            if params.get(key):
                self.storage[self.key][chat_id]['data'][key] = params[key]

    def pop(self, chat_id: int) -> dict:
        value = self.storage[self.key].pop(chat_id)
        return value['data']
