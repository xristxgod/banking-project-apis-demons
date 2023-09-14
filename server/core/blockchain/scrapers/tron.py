import decimal

from core.blockchain.scrapers.base import Message, Participant
from core.blockchain.scrapers.base import AbstractTransactionScraper


class TransactionScraper(AbstractTransactionScraper):
    async def get_transaction_commission(self, transaction: dict) -> tuple[decimal.Decimal, dict]:
        # TODO calculate fee
        pass

    async def scrape_transaction(self, transaction: dict, search_data: dict):
        if transaction['ret'][0]['contractRet'] != 'SUCCESS':
            return

        value = transaction['raw_data']['contract'][0]['parameter']['value']

        match transaction['raw_data']['contract'][0]['type']:
            case 'TransferContract':
                currency_id = None
                if value['to_address'] in search_data['direct_payments']:
                    order_id = search_data[value['to_address']]
                    amount = decimal.Decimal(repr(value['amount'] / 10 ** 6))
                    inputs = [Participant(address=value['owner_address'], amount=amount)]
                    outputs = [Participant(address=value['to_adddress'], amount=amount)]
                else:
                    return
            case 'TriggerSmartContract':
                if value['contract_address'] in search_data['provider_payments']:
                    pass
                elif value['contract_address'] in self.stable_coins:
                    pass

        fee, commission_detail = await self.get_transaction_commission(transaction=transaction)
        message = Message(
            timestamp=transaction['raw_data']['timestamp'],
            order_id=order_id,
            network_id=self.node.network.id,
            transaction_id=transaction['txID'],
            fee=fee,
            commission_detail=commission_detail,
            amount=amount,
            inputs=inputs,
            outputs=outputs,
            currency_id=currency_id,
        )

        return await self.send_to_task(message=message)
