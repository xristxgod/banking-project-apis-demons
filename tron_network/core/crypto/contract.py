import decimal

from tronpy.async_tron import AsyncTron, AsyncContract


class _Read:
    def __init__(self, contract: AsyncContract):
        pass


class _Write:
    def __init__(self, contract: AsyncContract):
        pass


class Contract:
    _cls_read = _Read
    _cls_write = _Write

    def __init__(self, address: str, decimal_place: int, symbol: str, name: str, node: AsyncTron):
        self.symbol, self.name = symbol.upper(), name
        self.address = address

        self.decimal_place = decimal_place
        self.contex = decimal.Context(prec=self.decimal_place)

        self._node = node

        self._contract = self._connect(address, node)

        self._read_contract = self._cls_read(self._contract)
        self._write_contract = self._cls_write(self._contract)

    def __str__(self):
        return f'Contract: {self.symbol}'

    @classmethod
    def _connect(cls, address: str, node: AsyncTron) -> AsyncContract:
        from tronpy.providers import HTTPProvider

        temp_provider = HTTPProvider(node.provider.endpoint_uri)
        response = temp_provider.make_request(
            "wallet/getcontract",
            {
                "value": address,
                "visible": True
            }
        )
        return AsyncContract(
            address,
            bytecode=response.get('bytecode', ''),
            name=response.get('name', ''),
            abi=response.get('abi', {}).get('entrys', []),
            origin_energy_limit=response.get('origin_energy_limit', 0),
            user_resource_percent=response.get('consume_user_resource_percent', 100),
            origin_address=response.get('code_hash', ''),
            client=node
        )

    @property
    def read(self) -> _Read:
        return self._read_contract

    @property
    def write(self) -> _Write:
        return self._write_contract
