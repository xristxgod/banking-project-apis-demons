from __future__ import annotations

import decimal
from typing import Coroutine

import settings
from core.blockchain.scrapers.base import TransactionType
from core.blockchain.scrapers.base import Message, Participant
from core.blockchain.scrapers.base import AbstractTransactionScraper

PROVIDER_METHODS = {}


async def get_input_native_transaction_handler(scraper: TransactionScraper, search_data: dict,
                                               tx_id: str, value: dict, timestamp: int) -> Message:
    fee, commission_detail = await scraper.get_transaction_commission(tx_id=tx_id)
    amount = decimal.Decimal(repr(value['amount'] / 10 ** scraper.node.network.native_decimal_place))

    return Message(
        timestamp=timestamp,
        order_id=search_data['direct_payments'][value['to_address']],
        network_id=scraper.node.network.id,
        transaction_id=tx_id,
        fee=fee,
        commission_detail=commission_detail,
        amount=amount,
        inputs=[Participant(
            address=value['owner_address'],
            amount=amount,
        )],
        outputs=[Participant(
            address=value['to_address'],
            amount=amount
        )],
    )


async def get_input_stable_coin_transaction_handler(scraper: TransactionScraper, search_data: dict,
                                                    tx_id: str, value: dict, timestamp: int) -> Message:
    fee, commission_detail = await scraper.get_transaction_commission(tx_id=tx_id)
    # TODO
    to_address, raw_amount = scraper.node.decode_data('', value['data'])
    if order_id := search_data['direct_payments'].get(to_address):
        currency_id, decimal_place = scraper.stable_coins[value['contract_address']]
        amount = decimal.Decimal(repr(raw_amount / 10 ** decimal_place))
        return Message(
            timestamp=timestamp,
            order_id=order_id,
            network_id=scraper.node.network.id,
            transaction_id=tx_id,
            fee=fee,
            commission_detail=commission_detail,
            amount=amount,
            inputs=[Participant(
                address=value['owner_address'],
                amount=amount,
            )],
            outputs=[Participant(
                address=to_address,
                amount=amount
            )],
            currency_id=currency_id,
        )


async def get_input_provider_transaction_handler(scraper: TransactionScraper,
                                                 tx_id: str, value: dict, timestamp: int, **kwargs) -> Message:

    fee, commission_detail = await scraper.get_transaction_commission(tx_id=tx_id)
    decoded_data = scraper.node.decode_data(PROVIDER_METHODS[value['data'][:8]])

    if len(decoded_data) == 2:
        currency_id = None
        amount = decimal.Decimal(repr(value['amount'] / 10 ** scraper.node.network.native_decimal_place))
    else:
        currency_id, decimal_place = scraper.stable_coins[value['contract_address']]
        amount = decimal.Decimal(repr(decoded_data[1] / 10 ** decimal_place))

    return Message(
        timestamp=timestamp,
        order_id=decoded_data[0],
        network_id=scraper.node.network.id,
        transaction_id=tx_id,
        fee=fee,
        commission_detail=commission_detail,
        amount=amount,
        inputs=[Participant(
            address=value['owner_address'],
            amount=amount,
        )],
        outputs=[Participant(
            address='',  # TODO
            amount=amount
        )],
        currency_id=currency_id
    )


HANDLER: dict[int: Coroutine] = {
    TransactionType.INPUT_NATIVE_TRANSACTION: get_input_native_transaction_handler,
    TransactionType.INPUT_STABLE_COIN_TRANSACTION: get_input_stable_coin_transaction_handler,
    TransactionType.INPUT_PROVIDER_TRANSACTION: get_input_provider_transaction_handler,
}


class TransactionScraper(AbstractTransactionScraper):
    async def get_transaction_commission(self, tx_id: str) -> tuple[decimal.Decimal, dict]:
        # TODO calculate fee
        pass

    async def scrape_transaction(self, transaction: dict, search_data: dict):
        if transaction['ret'][0]['contractRet'] != 'SUCCESS':
            return

        value = transaction['raw_data']['contract'][0]['parameter']['value']

        match transaction['raw_data']['contract'][0]['type']:
            case 'TransferContract':
                if search_data['direct_payments'].get(value['to_address']):
                    handler = HANDLER[TransactionType.INPUT_NATIVE_TRANSACTION]
                else:
                    return None
            case 'TriggerSmartContract':
                if value['contract_address'] in search_data['provider_payments'] and value['data'][:8] in ['', '']: # TODO
                    handler = HANDLER[TransactionType.INPUT_PROVIDER_TRANSACTION]
                elif value['contract_address'] in self.stable_coins and value['data'][:8] == 'a9059cbb':
                    handler = HANDLER[TransactionType.INPUT_STABLE_COIN_TRANSACTION]
                else:
                    return None
            case _:
                return None

        return await self.send_to_task(message=await handler(
            scraper=self,
            order_id=search_data,
            tx_id=transaction['txID'],
            value=value,
            timestamp=transaction['raw_data']['timestamp'],
        ))
