import os
from logging import getLogger
from decimal import Context, Decimal


decimal = Context()
decimal.prec = 9

ALL_TOKENS = "allToken.txt"

CONTRACT_MULTI_SEND = '0x957DA5Bdd1E80eA4Be7Cb9aF2469815A6754C1B8'
with open('files/multiSendABI.json', 'r') as f:
    CONTRACT_MULTI_SEND_ABI = f.read()

CONTRACT_TOKEN_SEND = '0xd2A78ee316Ea33a83C6ff183660F89875DD1594a'
with open('files/multiERC20ABI.json', 'r') as f:
    CONTRACT_TOKEN_SEND_ABI = f.read()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")
if "files" not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)
TOKENS = os.path.join(BASE_DIR, ALL_TOKENS)

# Logger
logger = getLogger(__name__)
