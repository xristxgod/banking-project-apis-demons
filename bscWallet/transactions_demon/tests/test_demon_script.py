from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, patch

from hexbytes import HexBytes

from src.demon import TransactionsDemon


contract_address = '0xBBc709564f70Fba250860f06E8b059eA54EEBa7A'.lower()


class TestDemonScript(IsolatedAsyncioTestCase):

    tx = {
        'blockHash': '0xda77e606b9c4576da10cf4248f2116210821de54f99d81a2195d686d9434b2a2',
        'blockNumber': 16641954,
        'from': '0x328130164d0f2b9d7a52edc73b3632e713ff0ec6',
        'gas': 25000000,
        'gasPrice': 20000000000,
        'hash': HexBytes.fromhex('976e41f8fa1dbad394166c70b578cfda4c74bab0210118a8abec96a7d5ee680a'),
        'input': '0xa9059cbb0000000000000000000000002ff6b5533241b093c43c5dfee086309713c1fa8400000000000000000000000000000000000000000000000f1f10190765375000',
        'nonce': 228062,
        'to': contract_address,
        'transactionIndex': 0,
        'value': 0,
        'type': '0x0',
        'v': 230,
        'r': '0x7cf149df7f6c4ad54a9720ed56957ea0741c010a1bdf883a4014f6abeade2cc2',
        's': '0x111cec8b97f47a342a8da689bf893471b78b700e1ef1c96578f4f8a34e5518bc'
    }
    addresses = ["0x328130164d0f2b9d7a52edc73b3632e713ff0ec6", "0x2ff6b5533241b093c43c5dfee086309713c1fa84", "0x55d398326f99059ff775485246999027b3197955"]
    timestamp = 1646815824000
    all_transactions_hash_in_db = []

    @patch('src.external_data.database.DB.get_tokens')
    async def test_get_node_block_number(self, get_tokens: Mock):
        get_tokens.return_value = []
        demon = TransactionsDemon()
        number = await demon.get_node_block_number()
        assert number != 0
        assert isinstance(number, int)

    @patch('src.external_data.database.DB.get_tokens')
    async def test_get_last_block_number(self, get_tokens: Mock):
        get_tokens.return_value = []
        demon = TransactionsDemon()
        number = await demon.get_node_block_number()
        assert number != 0
        assert isinstance(number, int)

    @patch('src.external_data.database.DB.get_tokens')
    async def test_smart_contract_transaction(self, get_tokens: Mock):
        get_tokens.return_value = [
            (1, 'Tether USD', 'USDT', contract_address, 18, 'bsc', 'bsc_erc20_usdt')
        ]
        demon = TransactionsDemon()
        contract_info = await demon.processing_smart_contract(
            {
                'input': '0xa9059cbb0000000000000000000000002ff6b5533241b093c43c5dfee086309713c1fa8400000000000000000000000000000000000000000000000f1f10190765375000',
                'to': contract_address
            },
            tx_addresses=[]
        )

        assert isinstance(contract_info, dict)
        assert contract_info["recipients"][0]['address'] == "0x2ff6b5533241b093c43c5dfee086309713c1fa84"
        assert contract_info["token"] == "USDT"
        assert contract_info["amount"] == "278.939477640000000000"

    @patch('src.external_data.database.DB.get_tokens')
    @patch('src.external_data.es_send.__send_msg_to_kibana')
    async def test_processing_transaction(self, __send_msg_to_kibana: Mock, get_tokens: Mock):
        get_tokens.return_value = [
            (1, 'Tether USD', 'USDT', contract_address, 18, 'bsc', 'bsc_erc20_usdt')
        ]
        demon = TransactionsDemon()
        transaction = await demon._processing_transaction(
            TestDemonScript.tx, [int(x, 0) for x in TestDemonScript.addresses],
            TestDemonScript.timestamp, TestDemonScript.all_transactions_hash_in_db
        )

        assert transaction["address"] == TestDemonScript.addresses[0]
        assert len(transaction) == 2
        assert transaction["transactions"][0]["time"] == TestDemonScript.timestamp
        assert transaction["transactions"][0]["transactionHash"] == "0x976e41f8fa1dbad394166c70b578cfda4c74bab0210118a8abec96a7d5ee680a"
        assert transaction["transactions"][0]["amount"] == "278.939477640000000000"

        assert len(transaction["transactions"][0]["senders"]) == 1
        assert transaction["transactions"][0]["senders"][0] == {'address': '0x328130164d0f2b9d7a52edc73b3632e713ff0ec6', 'amount': '278.939477640000000000'}
        assert len(transaction["transactions"][0]["recipients"]) == 1
        assert transaction["transactions"][0]["recipients"][0] == {'address': '0x2ff6b5533241b093c43c5dfee086309713c1fa84', 'amount': '278.939477640000000000'}
        assert transaction["transactions"][0]["token"] == "USDT"
