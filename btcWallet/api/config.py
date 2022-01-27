from decimal import Context, Decimal
from logging import getLogger
import os


logger = getLogger(__name__)

decimal = Context()
decimal.prec = 8

ADMIN_ADDRESS = os.getenv('ADMIN_WALLET', '188c31hPxLcZekAG9JXZX97mDtshaqYC3z')
ADMIN_FEE = decimal.create_decimal(os.getenv('ADMIN_FEE', '0.00005'))

DUST_MULTIPLICATOR = int(os.getenv('DUST_MULTIPLICATOR', 2))

ACCOUNT_ADDRESS = os.getenv('ROOT_ADDRESS', '3KD18hMxhDANU21EEjPv8rzKZ36iZWUHnK')
MNEMONIC = os.getenv(
    'MNEMONIC',
    'belt source solution ship agent boss paper bean cherry melt promote puzzle'
)

X_ACCOUNT_PRIVATE_KEY = os.getenv(
    'X_ACCOUNT_PRIVATE_KEY',
    'xprv9xfhinWS5Qh2F5xCxofWFs51TAPZ1s697Vi88U2LPb8QmwkSHwP2UmfcAzVQWrLiD68gsGwoM8uwiRQ5Vxy9tGJiTe3fo6qFoDXs7Nzpn8K'
)
X_ACCOUNT_PUBLIC_KEY = os.getenv(
    'X_ACCOUNT_PUBLIC_KEY',
    'xpub6Bf48J3KunFKTa2g4qCWd11k1CE3RKozUidivrRwwvfPek5aqUhH2Zz62J48Ckg3u4qJzVtixh2B2JdPhDtFvtUiyjq7mTrjWrtV9pdybRs'
)

X_BIP32_PRIVATE_KEY = os.getenv(
    'X_BIP32_PRIVATE_KEY',
    'xprvA1x1UEJUHruGDBtfQ41Uhzife77gTkY1xiMjBY1emCCLLm5EcZCopXrgzagPKd1VBnED1Pn231GQ6DNUHzK6ubZHB6LZHKdaRG7SzkvWgRt'
)
X_BIP32_PUBLIC_KEY = os.getenv(
    'X_BIP32_PUBLIC_KEY',
    'xpub6EwMsjqN8ETZRfy8W5YV58fQC8xAsDFsKwHKyvRGKXjKDZQPA6X4NLBAqsfgGkYDkEu8JYbaokEmmb23veeJBoyejbfPoiCZWkXqvnrmwNe'
)

BIP32_ROOT_KEY = os.getenv(
    'BIP32_ROOT_KEY',
    'xprv9s21ZrQH143K3JwWduXTx3cWfJTDYDyGf6DQRv3MfR6r9Uqv1u92N3U27TQPCm8NcnHG3PYsBbWvt9iHrEiNYUKRHf52jEL2sJQwn2KuUQf'
)

ROOT_PUB_KEY = os.getenv(
    'ROOT_PUB_KEY',
    '03faf30947b9491f1558e66d7b13b15227bee6b707a8bcfd57e075c27b25b64111'
)
ROOT_PRIVATE_KEY = os.getenv(
    'ROOT_PRIVATE_KEY',
    'f92cb73e696320a5ea5ab396e341ed9b9030e4cc47900d7dc9fef9270e15705c'
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, 'files')

if 'files' not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)

SUB_WALLET_INDEX_FILE = os.path.join(BASE_DIR, 'walletIndex.txt')

if 'walletIndex.txt' not in os.listdir(BASE_DIR):
    with open(SUB_WALLET_INDEX_FILE, 'w') as file:
        file.write('1')
