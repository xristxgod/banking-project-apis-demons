import requests
from src.node import btc


def is_node_alive():
    try:
        response = requests.get(f'https://blockchain.info/latestblock')
        public_block = response.json()['height']
        node_block = int(btc.rpc_host.getblockcount())
        return public_block - node_block < 2
    except:
        return False
