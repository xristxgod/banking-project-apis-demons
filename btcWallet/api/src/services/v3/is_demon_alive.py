import requests
from config import NGINX_DOMAIN
from src.node import btc


def is_demon_alive():
    try:
        response = requests.get(f'{NGINX_DOMAIN}/get-last-block-file')
        text = response.text
        if not text.isdigit():
            return False
        inside_block = int(text)
        node_block = int(btc.rpc_host.getblockcount())
        return (node_block - inside_block) < 20
    except:
        return False
