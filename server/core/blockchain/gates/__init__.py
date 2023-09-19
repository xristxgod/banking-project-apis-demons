from .base import AbstractNode
from .tron import Node as TronNode
from .evm import Node as EVMNode

from core.blockchain.models import Network, NetworkFamily


def get_node(network: Network) -> AbstractNode:
    match network.family:
        case NetworkFamily.tron:
            return TronNode(network=network)
        case NetworkFamily.evm:
            return EVMNode(network=network)
        case _:
            raise ValueError('Node not found!')
