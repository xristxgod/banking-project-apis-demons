import os
import requests
from dotenv import load_dotenv

from solana.rpc.api import Client


load_dotenv()


class SolanaAPI:
    __URL = os.getenv('solanaApiUrl', "https://api.devnet.solana.com")

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(cls.__class__, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.client: Client = Client(SolanaAPI.__URL)


class TheBlockChainAPI:
    __URL = os.getenv('theblockchainapi', 'https://api.theblockchainapi.com/v1/solana/wallet')

    def __init__(self):
        headers = {
            'APIKeyID': os.getenv("APIKeyID"),
            'APISecretKey': os.getenv("APISecretKey")
        }
        self.client = requests.session()
        self.client.headers = headers

    def get(self, route: str, **params):
        return self.client.get(f'{TheBlockChainAPI.__URL}/{route}', params=params)

    def post(self, route: str, json: dict):
        return self.client.post(f'{TheBlockChainAPI.__URL}/{route}', json=json)


solana_api = SolanaAPI()
the_blockchain_api = TheBlockChainAPI()
