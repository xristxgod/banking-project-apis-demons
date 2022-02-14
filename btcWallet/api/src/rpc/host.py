import requests
from os import getenv

from hdwallet import BIP44HDWallet

from config import decimal, Decimal, logger
from .method import RPCMethod
from ..exceptions import BitcoinNodeException


class RPCHost:
    DEFAULT_TIMEOUT = 10

    __SATOSHI_IN_BTC = 10 ** 8

    __user: str = getenv("rpcUser", 'test')
    __password: str = getenv("rpcPass", 'test')
    __host: str = getenv("rpcHost", '127.0.0.1')
    __port: int = int(getenv("rpcPort", 8080))
    __wallet: str = getenv("rpcWallet", "prod_wallet")

    def __init__(self):
        self._session = requests.Session()
        self._url = f"http://{self.__user}:{self.__password}@{self.__host}:{self.__port}/wallet/{self.__wallet}"
        self._headers = {"content-type": "application/json"}
        self._session.verify = False

    def __getattr__(self, rpc_method):
        return RPCMethod(rpc_method, self)

    def get_all_transactions(self, address):
        """Get all transactions by address"""

        result = self.getreceivedbyaddress(address, 0)
        if len(result) > 0:
            return result[0]["txids"]
        return []

    def get_transactions_by_id(self, txid: str) -> dict:
        """Get full transaction"""
        return self.getrawtransaction(txid, True)

    def get_receipt_by_address(self, address: str) -> str:
        """Get all received bitcoins"""
        return self.getreceivedbyaddress(address)

    def get_btc_to_kb(self, to_confirm_within=2) -> int:
        """Get BTC/KB"""
        return round(Decimal(self.estimatesmartfee(to_confirm_within)["feerate"]), 8)

    def get_unspent(self, address):
        """Gets all unspent transaction outputs belonging to an address."""
        result = self.listunspent(0, 9999999, [address])
        return [
            [
                self.btc_to_satoshi(tx["amount"]),
                tx["confirmations"],
                tx["scriptPubKey"],
                tx["txid"],
                tx["vout"]
            ]
            for tx in result
        ]

    def get_balance(self, address):
        return sum([x[0] for x in self.get_unspent(address)])

    def create_raw_transaction(self, inputs: list, outputs: dict) -> str or bool:
        """
        Create a transaction spending the given inputs and creating new outputs.
        Outputs can be addresses or data.
        Returns hex-encoded raw transaction.
        Note that the transaction's inputs are not signed, and
        it is not stored in the wallet or transmitted to the network.
        :param inputs: The inputs
        :type inputs: list | [{"txid": "The transaction id", "vout": "The output number"}, ...]
        :param outputs: The outputs (key-value pairs), where none of the keys are duplicated.
        :type outputs: dict | {"address": amount, "the bitcoin address", the amount in BTC}
        """
        if not isinstance(inputs, list):
            inputs = list(inputs)
        if not isinstance(outputs, list):
            outputs = list(outputs)
        try:
            return self.createrawtransaction(inputs, outputs)
        except Exception as e:
            logger.error(e)
            return {'error': str(e)}

    def sign_raw_transaction(self, tx_hash: str, private_key: list) -> dict or bool:
        """
        Sign inputs for raw transaction (serialized, hex-encoded).
        The second argument is an array of base58-encoded private
        keys that will be the only keys used to sign the transaction.
        The third optional argument (may be null) is an array of previous transaction outputs that
        this transaction depends on but may not yet be in the block chain.
        :param tx_hash: The transaction hex
        :type tx_hash: str
        :param private_key: The base58-encoded private keys for signing
        :type private_key: list or str
        :return:
        """
        if not isinstance(private_key, list):
            private_key = [private_key]
        try:
            sing_trx = self.signrawtransactionwithkey(tx_hash, private_key)
        except Exception as e:
            logger.error(e)
            return {'error': str(e)}
        return sing_trx

    def send_raw_transaction(self, tx_hex, max_fee_rate):
        """
        Note that the transaction will be sent unconditionally to all peers, so using this
        for manual rebroadcast may degrade privacy by leaking the transaction's origin, as
        nodes will normally not rebroadcast non-wallet transactions already in their mempool.
        :param tx_hex: The hex string of the raw transaction
        :type tx_hex: str
        :param max_fee_rate: Reject transactions whose fee rate is higher than the specified value, expressed in BTC/kB.
        :type max_fee_rate: float | default=0.10
        :return:
        """
        try:
            tx_hash = self.sendrawtransaction(tx_hex, max_fee_rate)
        except BitcoinNodeException as e:
            logger.error(e)
            return False
        return tx_hash

    def decode_transaction(self, tx_hex: str) -> str:
        tx = self.decoderawtransaction(tx_hex)
        for index, out in enumerate(tx['vout']):
            tx['vout'][index]['value'] = '%.8f' % decimal.create_decimal(out['value'])
        return tx

    def btc_to_satoshi(self, amount: int) -> int:
        return int(self.__SATOSHI_IN_BTC * Decimal(amount))

    def import_wallet(self, wallet) -> bool:
        """Import wallet to node"""
        try:
            private_key = wallet.to_wif()
            public_key = wallet.pub_to_hex()
            address = wallet.segwit_address
            self.importaddress(address, "mango-bank", False)
            self.importprivkey(private_key, "mango-bank", False)
            self.importpubkey(public_key, "mango-bank", False)
            return True
        except Exception as e:
            logger.error(f'IMPORT WALLET ERROR: {e}')
            return False

    def is_trx_unspent(self, tx_id, v_out):
        try:
            return self.gettxout(tx_id, v_out)
        except Exception as e:
            raise e
            # return None
