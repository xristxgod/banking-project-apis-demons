from typing import Optional


class DepositStorage:
    # TODO add singleton meta-class
    def __init__(self):
        self.storage = {}

    def clear(self):
        self.storage.clear()

    def create(self, chat_id: int, params: Optional[dict] = None):
        if params:
            self.storage[chat_id] = params
        else:
            self.storage[chat_id] = dict(
                currency=None,
                amount=None,
            )
        return self.storage[chat_id]

    def update(self, chat_id: int, **values):
        self.storage[chat_id].update(values)

    def delete(self, chat_id: int):
        del self.storage[chat_id]
