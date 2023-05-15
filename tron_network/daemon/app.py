from tronpy.tron import TAddress

from core.crypto.node import Node
from daemon.daemon import TransactionDaemon


def create_daemon(node: Node, **kwargs):
    class Addresses:
        def __init__(self, addresses: list[TAddress]):
            self.addresses = addresses

        async def all(self) -> list[TAddress]:
            return self.addresses

    if isinstance(kwargs['addresses'], list):
        kwargs['addresses'] = Addresses(addresses=kwargs['addresses'])

    return TransactionDaemon(node=node, **kwargs,)
