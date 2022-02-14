import os
import json
import requests
from dotenv import load_dotenv

from config import decimal, Decimal, logger
from bit import PrivateKey, PrivateKeyTestnet
from mnemonic import Mnemonic
from hdwallet.cryptocurrencies import BitcoinMainnet, BitcoinTestnet
from hdwallet.hdwallet import BIP44HDWallet
from .rpc.host import RPCHost
from .utils import get_bip_key, convert_time
from .exceptions import BitcoinNodeException
from typing import List

load_dotenv()


class NodeBTC:
    testnet: bool = True if os.getenv("TestNet") == "True" else False

    def __init__(self):
        self.__rpc_host = RPCHost()

    @property
    def rpc_host(self):
        return self.__rpc_host

    def create_wallet(self, words: str = None) -> json:
        """Create Bitcoin wallet"""
        try:
            if not words:
                words: str = Mnemonic("english").generate(strength=128)

            keys = get_bip_key(words=words)
            if self.testnet:
                wallet = PrivateKeyTestnet(wif=keys.WalletImportFormat())
            else:
                wallet = PrivateKey(wif=keys.WalletImportFormat())

            return {
                "mnemonicPhrase": words,
                "privateKey": wallet.to_wif(),
                "publicKey": wallet.pub_to_hex(),
                "address": wallet.segwit_address,
            }
        except BitcoinNodeException as e:
            return {"error": e}

    def create_deterministic_wallet(self, words: str = None) -> json:
        """Create deterministic Bitcoin wallet"""
        try:
            if not words:
                words: str = Mnemonic("english").generate(strength=128)

            network = BitcoinTestnet if self.testnet else BitcoinMainnet

            wallet = BIP44HDWallet(
                cryptocurrency=network, account=0, change=False, address=0
            ).from_mnemonic(words, language="english")
            xprv = wallet.xprivate_key()
            wallet.clean_derivation()
            wallet.from_path(path="m/44'/0'/0'")
            account = {
                "accountPrivateKey": wallet.xprivate_key(),
                "accountPublicKey": wallet.xpublic_key(),
            }

            wallet.clean_derivation()
            wallet.from_path(path="m/44'/0'/0'/0")
            values = {
                **account,
                "rootXPrivateKey": xprv,
                "mnemonicPhrase": words,
                "BIP32RootKey": wallet.root_xprivate_key(),
                "privateKey": wallet.private_key(),
                "publicKey": wallet.public_key(),
                "address": wallet.p2sh_address(),
                "path": wallet.path(),
            }
            key = PrivateKey(wif=wallet.wif())
            btc.rpc_host.import_wallet(key)
            wallet.clean_derivation()
            return values
        except BitcoinNodeException as e:
            return {"error": e}

    def get_balance(self, private_key: str) -> dict:
        """Get balance by private_key"""
        wallet = PrivateKey(wif=private_key)
        self.__rpc_host.import_wallet(wallet)
        satoshi = wallet.get_balance()
        return {'balance': '%.8f' % (decimal.create_decimal(int(satoshi)) / (10**8))}

    def create_unsigned_transaction(self, inputs: list, outputs: dict) -> (dict, bool):
        """
        Create unsigned transaction
        :param inputs: The inputs
        :type inputs: list | [{"txid": "The transaction id", "vout": "The output number"}, ...]
        :param outputs: The outputs (key-value pairs), where none of the keys are duplicated.
        :type outputs: dict | {"address": amount, "the bitcoin address", the amount in BTC}
        :return:
        """
        try:
            create_tx_hex = self.__rpc_host.create_raw_transaction(inputs=inputs, outputs=outputs)
            if isinstance(create_tx_hex, bool):
                return {"error": ""}, False
            data = self.__rpc_host.decode_transaction(create_tx_hex)
            return {**data, 'createTxHex': create_tx_hex}, True
        except BitcoinNodeException as e:
            return {"error": e}, False

    def sign_and_send_transaction(self, private_keys: list, create_tx_hex, max_fee_rate: str) -> dict:
        """
        Sign and send transaction
        :param private_keys: The base58-encoded private keys for signing
        :type private_keys: list or str | ["privatekey", ...]
        :param create_tx_hex: Hex of created transaction
        :type create_tx_hex: str | "sdfg124rtbGv34en6...hdvg1144ktb54e1nx"
        :param max_fee_rate: Reject transactions whose fee rate is higher than the specified value, expressed in BTC/kB.
        :type max_fee_rate: float | str | default=0.10
        :return:
        """
        try:
            try:
                sign_tx_hax = self.__rpc_host.sign_raw_transaction(
                    tx_hash=create_tx_hex,
                    private_key=private_keys
                )
            except Exception as e:
                return {"error": f'Cant sign: {e}'}
            if type(sign_tx_hax) == bool:
                return {"error": "Can't sign transaction'"}

            try:
                send_trx_hash = self.__rpc_host.send_raw_transaction(
                    tx_hex=sign_tx_hax["hex"],
                    max_fee_rate=max_fee_rate
                )
            except Exception as e:
                return {"error": f"Can't send transaction: {e}. SIGNED: {sign_tx_hax}"}

            try:
                tx = self.__rpc_host.get_transactions_by_id(send_trx_hash)
            except Exception as e:
                return {'error': f'Cant get transaction after signing: {e}'}

            senders, amount = self.get_senders(tx['vin'])
            recipients, _ = self.get_recipients(tx['vout'])

            return {
                "time": None,
                "datetime": None,
                "transactionHash": tx['hash'],
                "amount": "%.8f" % amount,
                "fee": "%.8f" % (
                        decimal.create_decimal(max_fee_rate)
                        * decimal.create_decimal(tx['size'])
                        / decimal.create_decimal(1000)
                ),
                "senders": senders,
                "recipients": recipients
            }
        except Exception as e:
            return {"error": str(e)}

    def get_unspent(self, address):
        return self.__rpc_host.get_unspent(address=address)

    def get_optimal_fees(self, from_=1, to_=1, to_confirm_within=2) -> dict:
        """
        Get optimal fee for transaction
        :param from_: Number of inputs or list inputs
        :type from_: str, int, list, tuple
        :param to_: Number of outputs or list outputs
        :type to_: str, int, list, tuple
        :param to_confirm_within: Confirmation target in blocks (1 - 1008)
        :return: {"bytes": "...", "satoshi": "..."}
        """
        _btc_to_kb = self.__rpc_host.get_btc_to_kb(to_confirm_within=to_confirm_within)
        _btc_to_byte = _btc_to_kb / 1000
        _sat_to_kb = int(_btc_to_kb * 100000000)
        _sat_to_byte = _sat_to_kb / 1000
        _bytes_pre_transaction = 180 * from_ + 34 * to_ + 10 + from_
        _satoshi_pre_transaction = _bytes_pre_transaction * _sat_to_byte
        _btc_pre_transaction = Decimal(_satoshi_pre_transaction / 100000000)

        return {
            "transfer": "{} input -> {} output | Blocks {}".format(from_, to_, to_confirm_within),
            "BTC/KB": "%.8f" % _btc_to_kb,
            "BTC/BYTE": "%.8f" % _btc_to_byte,
            "SAT/KB": "%.8f" % _sat_to_kb,
            "SAT/BYTE": "%.8f" % _sat_to_byte,
            "bytes": str(_bytes_pre_transaction),
            "satoshi": str(int(_satoshi_pre_transaction)),
            "btc": "%.8f" % round(_btc_pre_transaction, 8)
        }

    def get_receipt_at_address(self, address: str) -> json:
        """Get all received bitcoins"""
        try:
            return {"totalReceived": str(self.__rpc_host.get_receipt_by_address(address=address))}
        except BitcoinNodeException as e:
            return {"error": e}

    def get_sent_at_address(self, address: str) -> json:
        """Receive all sent bitcoins"""
        try:
            data = requests.get("https://blockchain.info/rawaddr/" + address).json()['total_sent']
        except requests.exceptions.ConnectionError:
            return {"totalSent": 0}
        return {"totalSent": str(data)}

    def get_tx_by_id(self, tx_id: int):
        trx = self.__rpc_host.get_transactions_by_id(tx_id)
        # Exclude not
        if "blocktime" not in trx.keys():
            return None

        addresses_from, amount_from = self.get_senders(trx["vin"])
        addresses_to, amount_to = self.get_recipients(trx["vout"])
        fee = amount_from - amount_to

        logger.error(f'GET TX FOR ADDRESS: {trx["txid"]} : {amount_from}')
        return {
            "time": trx["blocktime"],
            "datetime": convert_time(trx["blocktime"]),
            "transactionHash": trx["txid"],
            "amount": "%.8f" % amount_from,
            "amountBTC": "%.8f" % amount_from,
            "fee": "%.8f" % fee,
            "senders": addresses_from,
            "recipients": addresses_to
        }

    def get_unspent_transactions_by_address(self, address: str) -> List[dict]:
        trx_for_address = []
        trx_all = btc.rpc_host.listunspent(0, 99999999, [address])
        for tx in trx_all:
            trx = self.get_tx_by_id(tx['txid'])
            # Exclude not
            if trx is None:
                continue
            trx_for_address.append(trx)
        return trx_for_address

    def get_transactions_by_private_key(self, private_key: str) -> List[dict]:
        wallet = PrivateKey(wif=private_key)
        self.__rpc_host.import_wallet(wallet)

        trx_all = wallet.get_transactions()
        trx_for_address = []
        for trx_id in trx_all:
            trx = self.get_tx_by_id(trx_id)
            # Exclude not
            if trx is None:
                continue

            logger.error(f'GET TX FOR ADDRESS: {trx["transactionHash"]} : {trx["amount"]}')
            trx_for_address.append(trx)
        return trx_for_address

    def get_all_transactions(self, addresses) -> json:
        try:
            addresses_back = []

            if isinstance(addresses, str):
                addresses = [addresses]

            for address in addresses:
                trx_for_address = self.get_unspent_transactions_by_address(address)
                addresses_back.append({
                    "address": address,
                    "transactions": trx_for_address
                })

            return addresses_back
        except BitcoinNodeException as e:
            return {"error": e}

    def get_senders(self, vin: list):
        """ Get the input addresses and the sum of the output """
        full = []
        amount = decimal.create_decimal(0)
        for v in vin:
            try:
                inp = self.__rpc_host.getrawtransaction(v["txid"], True)
                values = inp["vout"][int(v["vout"])]
                current_amount = decimal.create_decimal(values["value"])
                amount += current_amount
                full.append({
                    "address": values["scriptPubKey"]["addresses"][0],
                    "amount": "%.8f" % current_amount,
                    "amountBTC": "%.8f" % current_amount,
                })
            except Exception as e:
                logger.error(f'GET SENDERS: {e}')
                continue
        return full, amount

    def get_recipients(self, vout: list) -> tuple:
        """ Get output address and amount """
        full = []
        amount = decimal.create_decimal(0)
        for v in vout:
            try:
                current_amount = decimal.create_decimal(v["value"])
                amount += current_amount
                full.append({
                    "address": v["scriptPubKey"]["addresses"][0],
                    "amount": "%.8f" % current_amount,
                    "amountBTC": "%.8f" % current_amount,
                    "n": v["n"]
                })
            except Exception as e:
                logger.error(f'GET RECIPIENTS: {e}')
                continue
        return full, amount


btc = NodeBTC()
