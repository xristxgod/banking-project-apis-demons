from core.blockchain.scrapers.base import Message, Participant
from core.blockchain.scrapers.base import AbstractTransactionScraper


class TransactionScraper(AbstractTransactionScraper):
    async def scrape_transaction(self, transaction: dict, search_data: dict):
        if transaction['ret'][0]['contractRet'] != 'SUCCESS':
            return

        value = transaction['raw_data']['contract'][0]['parameter']['value']

        match transaction['raw_data']['contract'][0]['type']:
            case 'TransferContract':
                if value['to_address'] in search_data['direct_payments']:
                    pass
                pass
            case 'TriggerSmartContract':
                if value['contract_address'] in search_data['provider_payments']:
                    pass
                pass
