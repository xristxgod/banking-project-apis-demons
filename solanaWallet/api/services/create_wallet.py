from schemas import BodyCreateWallet, CreateWalletResponse
from clients import the_blockchain_api


def create_wallet(body: BodyCreateWallet) -> CreateWalletResponse:
    phrase, is_success = __create_secret_phrase()
    if not is_success:
        return {'error': phrase}
    public_key, is_success = __create_public_key(words=phrase, secret_word=body.secret_word)
    if not is_success:
        return {'error': public_key}

    return CreateWalletResponse(
        MnemonicPhrase=phrase,
        PublicKey=public_key,
        SecretWord=body.secret_word
    )


def __create_secret_phrase() -> (str, bool):
    try:
        response = the_blockchain_api.post('secret_recovery_phrase', json={})
        return response.json()['secret_recovery_phrase'], True
    except Exception as e:
        return f"Didn't generate. Error: {e}", False


def __create_public_key(words: str, secret_word: str) -> (str, bool):
    """ This method generates a public key from words """
    try:
        response = the_blockchain_api.post('public_key', json={
            "secret_recovery_phrase": words,
            "derivation_path": the_blockchain_api.derivation_path,
            "passphrase": secret_word
        })
        return response.json()['public_key'], True
    except Exception as e:
        return f"Can't create public key. Error: {e}", False


def __create_address_nft(public_key: str, network: str) -> str:
    """ See the NFTs that belong to a given public key address """
    response = the_blockchain_api.get('nfts', json={
        "public_key": public_key,
        "network": network,
        "candy_machine_id": the_blockchain_api.candy_machine_id
    })
    return response.json()['$ref']
