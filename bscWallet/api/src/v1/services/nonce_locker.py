from asyncio import Lock

nonce_iterator_lock = Lock()

class NonceLocker:
    def __init__(self):
        self.nonce = None


nonce_locker = NonceLocker()
