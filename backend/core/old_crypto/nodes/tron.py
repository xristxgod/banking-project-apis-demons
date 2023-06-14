from core.old_crypto import models
from core.old_crypto.nodes.base import AbstractNode
from core.old_crypto.currency.tron import Native, StableCoin
from core.old_crypto.transaction.tron import Transaction


class Node(AbstractNode):
    network_pk = 1

    cls_native = Native
    cls_stable_coin = StableCoin

    cls_transaction = Transaction

    @classmethod
    def _pre_init(cls, network: models.Network) -> tuple:
        from tronpy.tron import Tron, HTTPProvider
        provider = HTTPProvider(
            endpoint_uri=network.url,
        )
        return provider, Tron(provider=provider)

    @classmethod
    def connect_to_contract(cls, address: str, client):
        return client.get_contract(address)
