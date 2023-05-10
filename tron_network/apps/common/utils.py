import string
import secrets

from mnemonic import Mnemonic
from pydantic import ValidationError
from tronpy.tron import TAddress
from tronpy.keys import is_address, to_base58check_address


def generate_mnemonic():
    return Mnemonic('english').generate(128)


def generate_passphrase():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(6))


def correct_address(address: TAddress):
    if not is_address(address):
        raise ValidationError(f'Address: {address} is not correct')
    return to_base58check_address(address)
