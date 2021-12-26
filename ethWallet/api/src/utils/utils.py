import json

from ecdsa.curves import SECP256k1
from eth_utils import to_checksum_address, keccak as eth_utils_keccak
from datetime import datetime


ERC20_ABI = json.loads(
    '[{"constant": true, "inputs": [], "name": "name", "outputs": [{"name": "", "type": '
    '"string"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{"name": '
    '"_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", '
    '"outputs": [{"name": "success", "type": "bool"}], "payable": false, "type": "function"}, '
    '{"constant": true, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", '
    '"type": "uint256"}], "payable": false, "type": "function"}, {"constant": false, "inputs": [{'
    '"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", '
    '"type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "success", '
    '"type": "bool"}], "payable": false, "type": "function"}, {"constant": true, "inputs": [], '
    '"name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "payable": false, '
    '"type": "function"}, {"constant": true, "inputs": [{"name": "", "type": "address"}], '
    '"name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "payable": false, '
    '"type": "function"}, {"constant": true, "inputs": [], "name": "owner", "outputs": [{"name": '
    '"", "type": "address"}], "payable": false, "type": "function"}, {"constant": true, '
    '"inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "payable": '
    'false, "type": "function"}, {"constant": false, "inputs": [{"name": "_to", '
    '"type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": ['
    '], "payable": false, "type": "function"}, {"constant": true, "inputs": [{"name": "", '
    '"type": "address"}, {"name": "", "type": "address"}], "name": "allowance", "outputs": [{'
    '"name": "", "type": "uint256"}], "payable": false, "type": "function"}]'
)


class PublicKey:
    BIP32_CURVE = SECP256k1

    def __init__(self, private_key: str):
        self.__point = int.from_bytes(private_key, byteorder='big') * self.BIP32_CURVE.generator

    def __bytes__(self):
        x_str = self.__point.x().to_bytes(32, byteorder='big')
        parity = self.__point.y() & 1
        return (2 + parity).to_bytes(1, byteorder='big') + x_str

    def address(self):
        x = self.__point.x()
        y = self.__point.t()
        s = x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
        return to_checksum_address(eth_utils_keccak(s)[12:])


def convert_time(t: int) -> str:
    return datetime.fromtimestamp(int(t)).strftime('%Y-%m-%d %H:%M:%S')
