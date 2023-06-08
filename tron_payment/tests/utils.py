from __future__ import annotations

import uuid
import time
import random
import decimal
from collections import namedtuple

from faker.providers import BaseProvider
from faker.providers.currency.en_US import Provider
from tronpy.keys import PrivateKey
from tronpy.abi import trx_abi

from core.schemas import TransactionType


class TronProvider(Provider, BaseProvider):

    FakeStableCoin = namedtuple('FakeStableCoin', field_names=[
        'address', 'symbol', 'name', 'decimal_place',
    ])

    @staticmethod
    def _random_private_key_obj():
        return PrivateKey.random()

    def tron_private_key(self) -> str:
        return self._random_private_key_obj().hex()

    def tron_address(self) -> str:
        return self._random_private_key_obj().public_key.to_base58check_address()

    def tron_stable_coin(self):
        symbol, name = self.cryptocurrency()
        return self.FakeStableCoin(
            address=self.tron_address(),
            symbol=symbol,
            name=name,
            decimal_place=random.randint(6, 18),
        )


class FakeRawTransaction:
    ret = [{
        'contractRet': 'SUCCESS'
    }]
    signature = [
        '0' * 130
    ]
    raw_data = {
        "contract": [{
            "parameter": {"value": None, "type_url": "type.googleapis.com/protocol.{type}"},
            "type": None,
        }],
        "timestamp": int(time.time()),
        "expiration": int(time.time()) + 60_000,
        "ref_block_bytes": None,
        "ref_block_hash": None,
        "fee_limit": random.randint(10**8, 10**18),
    }
    raw_data_hex = '---'

    def __init__(self, owner: str, amount: decimal.Decimal, typ: TransactionType, is_signed: bool = True, **params):
        self.owner = owner
        self.amount = amount
        self.type = typ

        self.raw_transaction = None

        for key, value in params.items():
            setattr(self, key, value)

        self.build(is_signed)

    def _generate_fake_data(self):
        match self.type:
            case TransactionType.TRANSFER | TransactionType.APPROVE:
                method = 'a9059cbb' if self.type == TransactionType.TRANSFER else '095ea7b3'
                data_without_method = trx_abi.encode_single('(address,uint256)', [self.to_address, self.amount])
            case TransactionType.TRANSFER_FROM:
                method = '23b872dd'
                data_without_method = trx_abi.encode_single('(address,address,uint256)', [
                    self.from_address, self.to_address, self.amount
                ])
            case _:
                raise ValueError()

        return method + data_without_method.hex()

    def _build(self, raw_data: dict, signature: list):
        self.raw_transaction = {
            'ret': self.ret,
            'signature': signature,
            'txID': uuid.uuid4().hex,
            'raw_data': raw_data,
            'raw_data_hex': self.raw_data_hex,
        }

    def build(self, is_signed: bool):

        match self.type:
            case TransactionType.TRANSFER:
                if hasattr(self, 'contract_address'):
                    typ = 'TriggerSmartContract'
                    value = {
                        'owner_address': self.owner,
                        'contract_address': self.contract_address,
                        'data': self._generate_fake_data(),
                    }
                else:
                    typ = 'TransferContract'
                    value = {
                        'owner_address': self.owner,
                        'to_address': self.to_address,
                        'amount': self.amount,
                    }
            case TransactionType.FREEZE:
                if hasattr(self, 'receiver_address'):
                    typ = 'DelegateResourceContract'
                    value = {
                        'owner_address': self.owner,
                        'receiver_address': self.receiver_address,
                        'balance': self.amount,
                        'resource': self.resource,
                    }
                else:
                    typ = 'DelegateResourceContract'
                    value = {
                        'owner_address': self.owner,
                        'frozen_balance': self.amount,
                        'resource': self.resource,
                    }
            case TransactionType.UNFREEZE:
                if hasattr(self, 'to_address'):
                    typ = 'UnDelegateResourceContract'
                    value = {
                        'owner_address': self.owner,
                        'receiver_address': self.to_address,
                        'balance': self.amount,
                        'resource': self.resource,
                    }
                else:
                    typ = 'DelegateResourceContract'
                    value = {
                        'owner_address': self.owner,
                        'unfreeze_balance': self.amount,
                        'resource': self.resource,
                    }
            case TransactionType.APPROVE | TransactionType.TRANSFER_FROM:
                typ = 'TriggerSmartContract'
                value = {
                    'owner_address': self.owner,
                    'contract_address': self.contract_address,
                    'data': self._generate_fake_data(),
                }
            case _:
                raise ValueError()

        raw_data = self.raw_data.copy()
        raw_data['contract'][0]['parameter']['value'] = value
        raw_data['contract'][0]['parameter']['type_url'].format(type=typ)
        raw_data['contract'][0]['type'] = typ

        self._build(raw_data, signature=self.signature if is_signed else [])

    @property
    def result(self) -> dict:
        return self.raw_transaction
