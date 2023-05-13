from core.crypto.node import Node

from daemon.daemon import TransactionDaemon


def create_daemon(node: Node):
    return TransactionDaemon(
        node=node,
    )
