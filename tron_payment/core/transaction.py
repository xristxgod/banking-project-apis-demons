import enum
import asyncio
import decimal
import functools
from typing import Self, Optional

import trontxsize
from tronpy.abi import trx_abi
from tronpy.keys import PrivateKey
from tronpy.async_tron import AsyncTron, AsyncTransactionBuilder, AsyncTransaction
from tronpy.exceptions import AddressNotFound

import settings
from core import schemas
from core.utils import from_sun
from core.schemas import TransactionType

SMART_CONTRACT_TRANSACTION_TYPES = {
    'a9059cbb': ('transfer', '(address,uint256)', TransactionType.TRANSFER),
    '095ea7b3': ('approve', '(address,uint256)', TransactionType.APPROVE),
    '23b872dd': ('transferFrom', '(address,address,uint256)', TransactionType.TRANSFER_FROM),
}

TRANSACTION_TYPES = {
    'TransferContract': TransactionType.TRANSFER,
    'FreezeBalanceV2Contract': TransactionType.FREEZE,
    'DelegateResourceContract': TransactionType.FREEZE,
    'UnfreezeBalanceV2Contract': TransactionType.UNFREEZE,
    'UnDelegateResourceContract': TransactionType.UNFREEZE,
}


class Transaction:
    class TransactionTypeNotFound(Exception):
        pass

    @staticmethod
    @functools.lru_cache(None)
    def decode_data(data: str) -> tuple[tuple, str]:
        _, parameter, typ = SMART_CONTRACT_TRANSACTION_TYPES[data[:8]]
        return trx_abi.decode_single(parameter, data[8:]), typ

    @classmethod
    async def commission(cls, raw_data: dict, signature: str, client: AsyncTron) -> schemas.Commission:
        if raw_data['contract'][0]['type'] == 'TransferContract':
            from core.node import node

            if not await node.is_active_address(
                    client.to_base58check_address(raw_data['contract'][0]['parameter']['value']['to_address'])
            ):
                return schemas.Commission(
                    amount=decimal.Decimal(1.1),
                    bandwidth=100,
                    energy=0,
                )

        bandwidth = trontxsize.get_tx_size({
            'raw_data': raw_data,
            'signature': [signature or '0' * 130],
        })

        energy = 0
        if raw_data['contract'][0]['parameter']['value'].get('data'):
            data = raw_data['contract'][0]['parameter']['value']['data']
            name, parameter, _ = SMART_CONTRACT_TRANSACTION_TYPES[data[:8]]

            owner_address = raw_data['contract'][0]['parameter']['value']['owner_address']
            contract_address = raw_data['contract'][0]['parameter']['value']['contract_address']

            constant_contract = await client.trigger_constant_contract(
                owner_address=owner_address,
                contract_address=contract_address,
                function_selector=name + parameter,
                parameter=data[8:],
            )
            energy = constant_contract['energy_used']

        amount = 0
        if bandwidth:
            amount += bandwidth * 400
        if energy:
            amount += energy * 1000

        return schemas.Commission(
            amount=from_sun(amount),
            bandwidth=bandwidth,
            energy=energy,
        )

    @classmethod
    async def make_response(cls, raw_transaction: dict, client: AsyncTron) -> schemas.TransactionBody:

        parameter = raw_transaction['raw_data']['contract'][0]['parameter']

        obj = schemas.TransactionBody
        typ = TRANSACTION_TYPES.get(parameter['type'])

        match typ:
            case TransactionType.TRANSFER:
                value = parameter['value']
                amount = from_sun(value['amount'])
                params = dict(
                    senders=[schemas.Participant(
                        address=value['owner_address'],
                        amount=amount,
                    )],
                    recipients=[schemas.Participant(
                        address=value['to_address'],
                        amount=amount,
                    )],
                    amount=amount,
                )
            case TransactionType.FREEZE | TransactionType.UNFREEZE:
                value = parameter['value']

                raw_amount = (
                    value.get('frozen_balance') or
                    value.get('unfreeze_balance') or
                    value.get('balance')
                )
                amount = from_sun(raw_amount)

                recipients = []
                if value.get('receiver_address'):
                    recipients.append(schemas.Participant(
                        address=value['receiver_address'],
                        amount=amount,
                    ))

                params = dict(
                    senders=[schemas.Participant(
                        address=value['owner_address'],
                        amount=amount,
                    )],
                    recipients=recipients,
                    amount=amount,
                )
            case _:
                # Smart contract transaction
                from core.node import node
                value = parameter['value']
                parameter, typ = cls.decode_data(parameter['data'])

                stable_coin = node.get_stable_coin(value['contract_address'])
                amount = stable_coin.to_decimal(parameter[-1])
                params = dict(
                    senders=[schemas.Participant(
                        address=value['owner_address'],
                        amount=amount,
                    )],
                    recipients=[],
                    amount=amount,
                    currency=stable_coin.symbol,
                )
                participant = schemas.Participant(
                    address=parameter[0],
                    amount=amount,
                )
                if len(parameter) == 2:
                    params['recipients'].append(participant)
                else:
                    params['senders'].append(participant)
                    params['recipients'].append(schemas.Participant(
                        address=parameter[1],
                        amount=amount,
                    ))

        commission = await cls.commission(raw_transaction['raw_data'], raw_transaction['signature'][0], client)

        return obj(
            timestamp=raw_transaction['timestamp'],
            commission=commission,
            type=typ,
            **params,
        )

    def __init__(self, transaction, client: AsyncTron):
        self.client = client
        self.transaction = transaction

    async def build(self, owner: str, **kwargs) -> Self:
        if asyncio.iscoroutinefunction(self.transaction):
            self.transaction = await self.transaction

        self.transaction = await self.transaction.with_owner(
            owner,
        ).fee_limit(
            kwargs.get('fee_limit') or settings.GLOBAL_FEE_LIMIT,
            ).build()

        return self

    def sign(self, private_key: str) -> Self:
        self.transaction = self.transaction.sign(priv_key=PrivateKey(
            private_key_bytes=bytes.fromhex(private_key),
        ))
        return self

    async def send(self, wait: bool = True) -> Self:
        if self.transaction.is_expired:
            await self.transaction.update()
        self.transaction = await self.transaction.broadcast()
        if wait:
            await self.transaction.wait()
        return self

    async def to_obj(self) -> Optional[schemas.TransactionBody]:
        return await self.make_response(self.transaction, self.client)
