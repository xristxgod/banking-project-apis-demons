"""
This test verifies the correctness of the script and its method.
# Check everything
python -m unittest test_demon_script.TestDemonScript
# Check the receipt of the last block number from the node.
python -m unittest test_demon_script.TestDemonScript.test_get_node_block_number
# Check to get the last block number from the file "last_block.txt".
python -m unittest test_demon_script.TestDemonScript.test_get_last_block_number
# Check the correctness of unpacking "data" during the token transaction
python -m unittest test_demon_script.TestDemonScript.test_smart_contract_transaction
# Check the correctness of the unpacking and packaging of the transaction.
python -m unittest test_demon_script.TestDemonScript.test_processing_transaction
"""
import unittest

from src.demon import TransactionsDemon


class TestDemonScript(unittest.IsolatedAsyncioTestCase):

    tx = {
        'blockHash': '0xda77e606b9c4576da10cf4248f2116210821de54f99d81a2195d686d9434b2a2',
        'blockNumber': 16641954,
        'from': '0x328130164d0f2b9d7a52edc73b3632e713ff0ec6',
        'gas': 25000000,
        'gasPrice': 20000000000,
        'hash': '0x5e8c8637c8a1422efac3b654d52c7f75bae5510011578f121b9260fbd76d60d7',
        'input': '0xa9059cbb0000000000000000000000002ff6b5533241b093c43c5dfee086309713c1fa8400000000000000000000000000000000000000000000000f1f10190765375000',
        'nonce': 228062,
        'to': '0x55d398326f99059ff775485246999027b3197955',
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

    async def test_get_node_block_number(self):
        demon = TransactionsDemon()
        number = await demon.get_node_block_number()
        self.assertNotEqual(number, 0)
        self.assertEqual(type(number), int)

    async def test_get_last_block_number(self):
        demon = TransactionsDemon()
        number = await demon.get_node_block_number()
        self.assertNotEqual(number, 0)
        self.assertEqual(type(number), int)

    async def test_smart_contract_transaction(self):
        demon = TransactionsDemon()
        contract_info = await demon.processing_smart_contract(
            {
                'input': '0xa9059cbb0000000000000000000000002ff6b5533241b093c43c5dfee086309713c1fa8400000000000000000000000000000000000000000000000f1f10190765375000',
                'to': '0x55d398326f99059ff775485246999027b3197955'
            },
            tx_addresses=[]
        )
        self.assertEqual(type(contract_info), dict)
        self.assertEqual(contract_info["to_address"], "0x2ff6b5533241b093c43c5dfee086309713c1fa84")
        self.assertEqual(contract_info["token"], "USDT")
        self.assertEqual(contract_info["amount"], "278.93947764")

    async def test_processing_transaction(self):
        demon = TransactionsDemon()
        transaction = await demon._processing_transaction(
            TestDemonScript.tx, TestDemonScript.addresses,
            TestDemonScript.timestamp, TestDemonScript.all_transactions_hash_in_db
        )
        self.assertEqual(transaction["address"], TestDemonScript.addresses[0])
        self.assertEqual(len(transaction), 2)
        self.assertEqual(transaction["transactions"][0]["time"], TestDemonScript.timestamp)
        self.assertEqual(transaction["transactions"][0]["transactionHash"], "0x5e8c8637c8a1422efac3b654d52c7f75bae5510011578f121b9260fbd76d60d7")
        self.assertEqual(transaction["transactions"][0]["amount"], "278.93947764")
        self.assertEqual(len(transaction["transactions"][0]["senders"]), 1)
        self.assertEqual(transaction["transactions"][0]["senders"][0], {'address': '0x328130164d0f2b9d7a52edc73b3632e713ff0ec6', 'amount': '278.93947764'})
        self.assertEqual(len(transaction["transactions"][0]["recipients"]), 1)
        self.assertEqual(transaction["transactions"][0]["recipients"][0], {'address': '0x2ff6b5533241b093c43c5dfee086309713c1fa84', 'amount': '278.93947764'})
        self.assertEqual(transaction["transactions"][0]["token"], "USDT")
