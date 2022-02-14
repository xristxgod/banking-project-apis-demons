from datetime import datetime
from mnemonic import Mnemonic
import bip32utils


def get_status(response: dict) -> int:
    if not isinstance(response, dict) or 'error' in response.keys():
        return 500
    return 200


def convert_time(t: int) -> str:
    return datetime.fromtimestamp(int(t)).strftime('%Y-%m-%d %H:%M:%S')


def get_bip_key(words: str):
    mob = Mnemonic("english")
    seed = mob.to_seed(words)
    bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
    bip32_child_key_obj = bip32_root_key_obj.ChildKey(
        44 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey(0).ChildKey(0)
    return bip32_child_key_obj
