from __future__ import absolute_import

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT_DIR / 'config'

CONTRACTS_DIR = CONFIG_DIR / 'contracts'
CONTRACTS_FILE = CONTRACTS_DIR / 'contracts.prod.json'
