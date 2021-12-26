from solana.publickey import PublicKey
from schemas import QueryBalance
from clients import solana_api


def get_balance(query: QueryBalance):
    return solana_api.client.get_balance(
        pubkey=PublicKey(query.pubkey),
        commitment=query.commitment
    )
