from typing import Optional


__all__ = (
    'take_central_wallet_info',
    'take_encode_secret_key',
)


class SecretStorage:
    @classmethod
    def get(cls, label: str) -> str:
        pass


def take_central_wallet_info(central_wallet_config: dict) -> dict:
    manager = central_wallet_config.get('manager')

    match manager:
        case 'SecretStorage':
            central_wallet_info = {
                'address': SecretStorage.get(central_wallet_config['wallet']['address']),
                'private_key': SecretStorage.get(central_wallet_config['wallet']['private_key']),
                'mnemonic': SecretStorage.get(central_wallet_config['wallet']['mnemonic']),
            }
        case None:
            central_wallet_info = central_wallet_config['wallet']
        case _:
            raise Exception('Central wallet not found!')

    return central_wallet_info


def take_encode_secret_key(encode_secret_key_config: dict, is_encode: bool) -> Optional[str]:
    if is_encode:
        return None

    manager = encode_secret_key_config.get('manager')

    match manager:
        case 'SecretStorage':
            encode_secret_key = SecretStorage.get(encode_secret_key_config.get('value'))
        case None:
            encode_secret_key = encode_secret_key_config['value']
        case _:
            raise Exception('Wallet secret key not found!')

    return encode_secret_key
