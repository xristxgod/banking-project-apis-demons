import abc
from typing import Type

from core.old_crypto import models
from core.old_crypto.currency.base import NativeInterface, StableCoinInterface
from core.old_crypto.transaction.base import TransactionInterface


class AbstractNode(metaclass=abc.ABCMeta):
    network_pk: int

    cls_native: Type[NativeInterface]
    cls_stable_coin: Type[StableCoinInterface]

    cls_transaction: Type[TransactionInterface]

    @abc.abstractclassmethod
    def _pre_init(cls, network: models.Network) -> tuple: ...

    @abc.abstractclassmethod
    def connect_to_contract(cls, address: str, client): ...

    def __init__(self):
        self.network = models.Network.objects.get(pk=self.network_pk)

        self.provider, self.client = self._pre_init(self.network)

        self.native = self.cls_native(client=self.client, obj=self.network)
        setattr(self, self.native.symbol, self.native)         # alias

        self.transaction = self.cls_transaction(client=self.client)

        self.stable_coins = {}

        self.setup()

    def update(self):
        stable_coins = models.StableCoin.objects.filter(
            network=self.network,
        )
        for stable_coin in models.StableCoin.objects.filter(network=self.network):
            self.stable_coins.update({
                stable_coin.pk: self.cls_stable_coin(
                    client=self.client,
                    contract=self.connect_to_contract(address=stable_coins.address, client=self.client),
                    obj=stable_coins,
                )
            })

    setup = update

    def get_stable_coin(self, pk: int) -> StableCoinInterface:
        return self.stable_coins[pk]

    def has_stable_coin(self, pk: int) -> bool:
        return self.stable_coins.get(pk) is not None
