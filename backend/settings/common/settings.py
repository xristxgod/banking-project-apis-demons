from __future__ import absolute_import

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
APPS_DIR = ROOT_DIR / 'apps'

TELEGRAM_BOT_TOKEN = ''
DOMAIN = ''

TESTNET = False

TELEGRAM_WEBHOOK_URL = DOMAIN + '/telegram-bot/webhook'

APPS_MODELS = [
    'apps.cryptocurrencies.models',
    'apps.telegram.models',
    'apps.wallets.models',
    'apps.orders.models',
]

DATABASE_URL = ''
