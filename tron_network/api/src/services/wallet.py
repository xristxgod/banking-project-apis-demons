from typing import Optional

from src.core import Node
from src.settings import settings


class Wallet:
    central_wallet = settings.CENTRAL_WALLET

    def __init__(self):
        self.core = Node()
        self.node = self.core.node
