import string
import secrets

from mnemonic import Mnemonic


def generate_mnemonic():
    return Mnemonic('english').generate(128)


def generate_passphrase():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(6))
