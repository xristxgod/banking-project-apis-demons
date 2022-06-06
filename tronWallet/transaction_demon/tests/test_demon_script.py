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

from src.demon import TransactionDemon
from config import USDT, USDC


class TestDemonScript(unittest.IsolatedAsyncioTestCase):

    tx = {
        "ret": [
            {
                "contractRet": "SUCCESS"
            }
        ],
        "signature": [
            "2b68d6fbe35df57ffc5ac90e63ab0eb46b60a73999a0d34b7a08d9b2e30983ea52c3f91fb179e69943cc0527e9251f81af7b4ee9c37e289f7e77a3e9ad49b27901"
        ],
        "txID": "1d6a287629efe5c0c511a69d31e87c07ee0cffb16773647d84e9412713abf9d5",
        "raw_data": {
            "contract": [
                {
                    "parameter": {
                        "value": {
                            "data": "a9059cbb00000000000000000000000084758bc3e1207e02279bd6eca4943f1cc5165c9a0000000000000000000000000000000000000000000000000000002c3ce1ec00",
                            "owner_address": "TTQQWvyoxM74ij1eksSUm9Yw9xT2fwEmNc",
                            "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                        },
                        "type_url": "type.googleapis.com/protocol.TriggerSmartContract"
                    },
                    "type": "TriggerSmartContract"
                }
            ],
            "ref_block_bytes": "5bd8",
            "ref_block_hash": "3faf55f6df27404b",
            "expiration": 1646815824000,
            "fee_limit": 40000000,
            "timestamp": 1646815766984
        },
        "raw_data_hex": "0a025bd822083faf55f6df27404b408091fdeef62f5aae01081f12a9010a31747970652e676f6f676c65617069732e636f6d2f70726f746f636f6c2e54726967676572536d617274436f6e747261637412740a1541bf3e264efe20122fcca794e1c13b655bd05cfb96121541a614f803b6fd780986a42c78ec9c7f77e6ded13c2244a9059cbb00000000000000000000000084758bc3e1207e02279bd6eca4943f1cc5165c9a0000000000000000000000000000000000000000000000000000002c3ce1ec0070c8d3f9eef62f900180b48913"
    }
    addresses = ["TN3b1cjcZvBrKMMWqqEJ9im9rp8DFmEKmj", "TKfLb1kZ7HMrXTPvTs9du2bZ3CwXoUpR72", "TFKN9Tgk9pzZUfMznYzPkBMBixpKCMzTMq"]
    timestamp = 1646815824000
    all_transactions_hash_in_db = []

    async def test_get_node_block_number(self):
        demon = TransactionDemon()
        number = await demon.get_node_block_number()
        self.assertNotEqual(number, 0)
        self.assertEqual(type(number), int)

    async def test_get_last_block_number(self):
        demon = TransactionDemon()
        number = await demon.get_last_block_number()
        self.assertNotEqual(number, 0)
        self.assertEqual(type(number), int)

    async def test_smart_contract_transaction(self):
        demon = TransactionDemon()
        data = "a9059cbb00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002c3e"
        usdt_contract = await demon.smart_contract_transaction(data=data, contract_address=USDT)
        usdc_contract = await demon.smart_contract_transaction(data=data, contract_address=USDC)
        self.assertEqual(type(usdt_contract), dict)
        self.assertEqual(type(usdc_contract), dict)
        self.assertEqual(usdt_contract["to_address"], "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb")
        self.assertEqual(usdc_contract["to_address"], "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb")
        self.assertEqual(usdt_contract["token"], "USDT")
        self.assertEqual(usdc_contract["token"], "USDC")
        self.assertEqual(usdt_contract["amount"], "0.01132600")
        self.assertEqual(usdc_contract["amount"], "0.01132600")

    async def test_processing_transaction(self):
        demon = TransactionDemon()
        transaction = await demon.processing_transaction(
            TestDemonScript.tx, TestDemonScript.addresses,
            TestDemonScript.timestamp, TestDemonScript.all_transactions_hash_in_db
        )
        self.assertEqual(transaction["address"], TestDemonScript.addresses[0])
        self.assertEqual(len(transaction), 2)
        self.assertEqual(transaction["transactions"][0]["time"], TestDemonScript.timestamp)
        self.assertEqual(transaction["transactions"][0]["transactionHash"], "1d6a287629efe5c0c511a69d31e87c07ee0cffb16773647d84e9412713abf9d5")
        self.assertEqual(transaction["transactions"][0]["amount"], "190000.00000000")
        self.assertEqual(transaction["transactions"][0]["fee"], "4.09668000")
        self.assertEqual(len(transaction["transactions"][0]["senders"]), 1)
        self.assertEqual(transaction["transactions"][0]["senders"][0], {'address': 'TTQQWvyoxM74ij1eksSUm9Yw9xT2fwEmNc', 'amount': '190000.00000000'})
        self.assertEqual(len(transaction["transactions"][0]["recipients"]), 1)
        self.assertEqual(transaction["transactions"][0]["recipients"][0], {'address': 'TN3b1cjcZvBrKMMWqqEJ9im9rp8DFmEKmj', 'amount': '190000.00000000'})
        self.assertEqual(transaction["transactions"][0]["token"], "USDT")
