
__all__ = (
    'take_central_wallet_info',
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
            central_wallet_info = central_wallet_config.get('wallet')

    return central_wallet_info
