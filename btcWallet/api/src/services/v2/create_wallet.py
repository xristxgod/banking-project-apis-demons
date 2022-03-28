from bit import PrivateKey

from src.node import btc
from hdwallet.cryptocurrencies import BitcoinMainnet, BitcoinTestnet
from hdwallet.hdwallet import BIP44HDWallet
from config import SUB_WALLET_INDEX_FILE, logger, BIP32_ROOT_KEY
from src.rpc.es_send import send_exception_to_kibana


def get_index() -> int:
    with open(SUB_WALLET_INDEX_FILE, 'r') as f:
        digit = int(f.read())
    return digit


def inc_index() -> int:
    digit = get_index()
    with open(SUB_WALLET_INDEX_FILE, 'w') as f:
        f.write(str(digit + 1))
    return digit


def create_sub_wallet():
    """Create Bitcoin wallet"""
    try:
        network = BitcoinTestnet if btc.testnet else BitcoinMainnet

        index = inc_index()

        wallet = BIP44HDWallet(
            cryptocurrency=network, account=0, change=False, address=0
        ).from_xprivate_key(BIP32_ROOT_KEY)
        wallet.clean_derivation()
        wallet.from_path(path=f"m/44'/0'/0'/0/{index}")
        new_wallet = {
            "privateKey": wallet.wif(),
            "publicKey": wallet.public_key(),
            "address": wallet.address(),
            "path": wallet.path(),
        }
        key = PrivateKey(wif=wallet.wif())
        btc.rpc_host.import_wallet(key)
        wallet.clean_derivation()
        return new_wallet
    except Exception as e:
        send_exception_to_kibana(e, 'ERROR CREATE HD')
        return {"error": str(e)}
