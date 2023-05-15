from __future__ import annotations

import asyncio
import logging
from typing import Optional

import aioredis
from tronpy.tron import TAddress
from tronpy.keys import to_base58check_address

import settings
from core import celery
from core.crypto.node import Node
from apps.transaction.schemas import TransactionType, BaseResponseSendTransactionSchema
from apps.transaction.utils import build_transaction as build_message

__all__ = (
    'TransactionDaemon',
)


class BlockController:

    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.client = aioredis.from_url(redis_url)

    def __str__(self):
        return 'daemon_block'

    async def get(self) -> int:
        return await self.client.get(self)

    async def save(self, number: int):
        await self.client.sadd(self, number)


class TransactionDaemon:
    find_type = [
        'TransferContract',
        'TriggerSmartContract',
        'FreezeBalanceV2Contract',
        'UnfreezeBalanceV2Contract',
        'DelegateResourceContract',
        'UnDelegateResourceContract',
    ]

    find_smart_contract_type = {
        'a9059cbb': TransactionType.TRANSFER,
        '095ea7b3': TransactionType.APPROVE,
        '23b872dd': TransactionType.TRANSFER_FROM,
    }

    from_balancer_valid_type = (
        TransactionType.TRANSFER,
        TransactionType.TRANSFER_NATIVE,
    )

    central_wallet_address = settings.CENTRAL_WALLET_CONFIG['address']

    @classmethod
    def _get_logger(cls) -> logging.Logger:
        pass

    def __init__(self, node: Node, **kwargs):
        self.node = node

        self.addresses = kwargs['addresses']
        self.block_controller = BlockController(redis_url=kwargs.get('redis_url'))

        self.balancer_on = kwargs.get('balancer_on', True)
        self.external_on = kwargs.get('external_on', True)

        self.logger = kwargs.get('logger') or self._get_logger()

    async def __call__(self, is_always: bool = True, **kwargs):
        if not is_always:
            return await self.start_in_range(**kwargs)

        start = await self.block_controller.get()
        while True:
            end = await self.node.client.get_latest_block_number()

            if end - start < 1:
                await asyncio.sleep(3)
                continue

            addresses = await self.addresses.all()

            success = await asyncio.gather(*[
                self.parsing_block(
                    number=start,
                    addresses=addresses,
                )
            ])
            self.logger.info(f'Block: start')

            if all(success):
                self.logger.info(f'Block: {start} :: Success')
                start += 1
                await self.block_controller.save(start)
            else:
                self.logger.error(f'Block: {start} :: Error')

    async def start_in_range(self, start: Optional[int] = None, end: Optional[int] = None, **kwargs):
        start = start or await self.node.client.get_latest_block_number() - 1
        end = end or await self.node.client.get_latest_block_number()

        for number in range(start, end + 1):
            self.logger.info(f'Parsing block: {number}')
            await self.parsing_block(number, await self.addresses.all())

    async def parsing_block(self, number: int, addresses: list[TAddress]) -> bool:
        block = await self.node.client.get_block(number)

        if len(block.get('transactions', [])) == 0:
            return True

        success = await asyncio.gather(*[
            self.parsing_transaction(
                transaction=transaction,
                addresses=addresses,
            )
            for transaction in block['transaction']
        ])

        return all(success)

    async def _get_addresses_in_data(self, data: str) -> tuple[TransactionType, list[TAddress]]:
        smart_contract_type = self.find_smart_contract_type.get(data[:8])

        match smart_contract_type:
            case TransactionType.TRANSFER:
                addresses = [to_base58check_address(f'41{data[32:72]}')]
            case TransactionType.APPROVE:
                # TODO
                addresses = []
            case TransactionType.TRANSFER_FROM:
                # TODO
                addresses = []
            case _:
                addresses = []

        return smart_contract_type, addresses

    async def _get_addresses_in_transaction(self,
                                            transaction_value: dict) -> tuple[Optional[TransactionType], list[TAddress]]:
        if transaction_value.get('to_address'):
            return TransactionType.TRANSFER_NATIVE, [transaction_value['to_address']]
        elif transaction_value.get('receiver_address'):
            return None, [transaction_value['receiver_address']]
        else:
            return await self._get_addresses_in_data(transaction_value['data'])

    async def pre_valid_transaction(self, transaction: dict) -> bool:
        if transaction["ret"][0]["contractRet"] != "SUCCESS":
            return False

        if transaction["raw_data"]["contract"][0]["type"] not in self.find_type:
            # Valid transaction type
            return False

        contract_address = transaction["raw_data"]["contract"][0]["parameter"]["value"].get('contract_address')
        if contract_address and not self.node.has_contract_address(contract_address):
            # If smart contract transaction, check validity of contract
            return False

    @staticmethod
    async def post_valid_transaction(addresses_in_transaction: list[TAddress], addresses: list[TAddress]) -> bool:
        for address in addresses_in_transaction:
            if address in addresses:
                return True
        else:
            return False

    async def parsing_transaction(self, transaction: dict, addresses: list[TAddress]) -> bool:
        if not await self.pre_valid_transaction(transaction):
            return True

        transaction_value = transaction["raw_data"]["contract"][0]["parameter"]["value"]

        from_address = transaction_value["owner_address"]
        transaction_type, to_addresses = self._get_addresses_in_transaction(transaction_value)

        if not self.post_valid_transaction([from_address, *to_addresses], addresses):
            return True

        return await self.make_request(
            message=build_message(transaction, transaction_type),
            addresses=addresses,
        )

    async def _make_request_to_internal(self, message: BaseResponseSendTransactionSchema, **kwargs) -> bool:
        if (
            self.balancer_on and
            message.type in self.from_balancer_valid_type and
            getattr(message, 'from_address') not in self.central_wallet_address and
            getattr(message, 'to_address') in kwargs['addresses']
        ):
            celery.app.send_task(
                'core.celery.tasks.balancer',
                kwargs=dict(
                    address=getattr(message, 'to_address'),
                    currency=getattr(message, 'currency', 'TRX'),
                )
            )

    async def _make_request_to_external(self, message: BaseResponseSendTransactionSchema, **kwargs) -> bool:
        # TODO
        pass

    async def make_request(self, message: BaseResponseSendTransactionSchema, **kwargs) -> bool:
        self.logger.info(f'Send message: {message.dict()}')
        return all([asyncio.gather(
            self._make_request_to_internal(message, **kwargs),
            self._make_request_to_external(message, **kwargs),
        )])
