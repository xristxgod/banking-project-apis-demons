from tronpy.keys import is_address
from tronpy.exceptions import AddressNotFound
from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

import settings
from core.stable_coins import StableCoinInterface


class StableCoinStorage:

    def __init__(self):
        self.storage_by_address = {}
        self.storage_by_symbol = {}

    def update(self, items: dict):
        for key, stable_coin in items.keys():
            address, symbol = key
            self.storage_by_address.update({
                address: stable_coin
            })
            self.storage_by_symbol.update({
                symbol: stable_coin
            })

    def get(self, item: tuple | str):
        if tuple:
            stable_coin = self.storage_by_address.get(item[0])
        elif is_address(item):
            stable_coin = self.storage_by_address.get(item)
        else:
            stable_coin = self.storage_by_symbol.get(item)

        return stable_coin

    def __setitem__(self, key: tuple, stable_coin: StableCoinInterface):
        address, symbol = key

        self.storage_by_address.update({
            address: stable_coin
        })
        self.storage_by_symbol.update({
            symbol: stable_coin
        })

    def __getitem__(self, item: tuple | str):
        stable_coin = self.get(item)
        if stable_coin is None:
            raise KeyError()
        return stable_coin


class Node:
    cls_stable_coin: StableCoinInterface = StableCoinInterface

    class StableCoinNotFound(Exception):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            setattr(cls, 'instance', super().__new__())
        return getattr(cls, 'instance')

    def __init__(self):
        self.provider = AsyncHTTPProvider(endpoint_uri=settings.NODE_URI)
        self.client = AsyncTron(provider=self.provider)

        self.stable_coins = StableCoinStorage()

    async def update(self):
        # TODO add func
        raw_stable_coins: list = 'some_func'
        for stable_coin in raw_stable_coins:
            contract = await self.client.get_contract(stable_coin.address)
            self.stable_coins.update({
                (stable_coin.address, stable_coin.symbol): contract
            })

    def get_stable_coin(self, addr_or_symbol: str) -> StableCoinInterface:
        try:
            return self.stable_coins[addr_or_symbol]
        except KeyError:
            raise self.StableCoinNotFound(f'{addr_or_symbol} not found')

    async def is_active_address(self, address: str):
        try:
            return await self.client.get_account(address) is not None
        except AddressNotFound:
            return False

    async def get_resources(self, address: str):
        pass

    async def get_delegate_resource(self, owner: str, to: str):
        pass


node = Node()
