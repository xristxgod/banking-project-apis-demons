from bit import PrivateKey
from src.node import btc


def import_wallet(private_key: str):
    try:
        wallet = PrivateKey(wif=private_key)
        return {'result': all([
            btc.rpc_host.importaddress(wallet.segwit_address, "mango-bank", False),
            btc.rpc_host.importprivkey(wallet.to_wif(), "mango-bank", False),
            btc.rpc_host.importpubkey(wallet.public_key, "mango-bank", False)
        ])}
    except:
        return {'result': False}
