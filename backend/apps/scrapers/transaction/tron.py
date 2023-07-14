from typing import Optional

from tronpy.abi import tron_abi

from src.caches.ram import cached

from apps.cryptocurrencies.nodes.tron import Node
from apps.scrapers.transaction.base import AbstractTransactionScraper


class TronTransactionScraper(AbstractTransactionScraper):
    @cached(60 * 5)
    def get_contract_addresses(self, orders: dict) -> list[str]:
        return [
            detail['currency'].address
            for pk, detail in orders.items()
            if not detail['currency'].is_native
        ]

    async def decoded_data(self, data: str) -> Optional[tuple]:
        match data[:8]:
            case 'a9059cbb':
                return tron_abi.decode(['address', 'uint256'], data[8:])
            case '':
                pass
            case '':
                pass

    async def parsing_transaction(self, transaction: dict, orders: dict, extra: dict):
        if transaction['ret'][0]['contractRet'] != "SUCCESS":
            return

        raw_data = transaction['raw_data']
        transaction_type = raw_data['contract'][0]['type']
        transaction_value = raw_data['contract'][0]['parameter']['value']

        match transaction_type:
            case 'TriggerSmartContract':
                contract_addresses = self.get_contract_addresses(orders)
                if transaction_value['contract_address'] in contract_addresses:
                    pass
                elif transaction_value['contract_address'] == self.order_provider.address:
                    pass
            case 'TransferContract':
                pass
