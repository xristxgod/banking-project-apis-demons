from unittest import TestCase
from unittest.mock import Mock, patch
from src.node import btc


class TestSignSendTransactionsCase(TestCase):
    @patch('src.rpc.es_send.__send_msg_to_kibana')
    @patch('src.node.RPCHost.get_transactions_by_id')
    @patch('src.node.RPCHost.send_raw_transaction')
    @patch('src.node.RPCHost.sign_raw_transaction')
    def test_sign_send_transaction_success(
            self,
            sign_raw_transaction: Mock,
            send_raw_transaction: Mock,
            get_transactions_by_id: Mock,
            __send_msg_to_kibana: Mock
    ):
        __send_msg_to_kibana.return_value = None
        sign_raw_transaction.return_value = {'hex': '123456789012345678901234567890123'}
        send_raw_transaction.return_value = {'hex': '123456789012345678901234567890123'}
        get_transactions_by_id.return_value = {
            'hash': 'hash', 'size': '119',
            'vin': [{
                "txid": "hex", "vout": 0, "scriptSig": {"asm": "str", "hex": "hex"}, "sequence": 0, "txinwitness": ["hex"]
            }],
            'vout': [{
                'value': 1000, 'n': 0, "scriptPubKey": {
                    "asm": "str", "hex": "str", "reqSigs": 0, "type": "str", 'pubkeyhash' "addresses": ["str"]
                }
            }]
        }
        sent_tx = btc.sign_and_send_transaction([], 'f', '0.00001')

        assert isinstance(sent_tx, dict)
        assert 'error' not in sent_tx.keys()

    @patch('src.node.RPCHost.get_transactions_by_id')
    @patch('src.node.RPCHost.send_raw_transaction')
    @patch('src.node.RPCHost.sign_raw_transaction')
    def test_sign_send_transaction_fail_sign(
            self,
            sign_raw_transaction: Mock,
            send_raw_transaction: Mock,
            get_transactions_by_id: Mock
    ):
        sign_raw_transaction.return_value = False
        send_raw_transaction.return_value = {'hex': '123456789012345678901234567890123'}
        get_transactions_by_id.return_value = {}
        sent_tx = btc.sign_and_send_transaction([], 'f', '0.00001')
        assert isinstance(sent_tx, dict)
        assert 'error' in sent_tx.keys()

    @patch('src.node.RPCHost.get_transactions_by_id')
    @patch('src.node.RPCHost.send_raw_transaction')
    @patch('src.node.RPCHost.sign_raw_transaction')
    def test_sign_send_transaction_fail_send(
            self,
            sign_raw_transaction: Mock,
            send_raw_transaction: Mock,
            get_transactions_by_id: Mock
    ):
        sign_raw_transaction.return_value = {'hex': '123456789012345678901234567890123'}
        send_raw_transaction.return_value = False
        get_transactions_by_id.return_value = {}
        sent_tx = btc.sign_and_send_transaction([], 'f', '0.00001')
        assert isinstance(sent_tx, dict)
        assert 'error' in sent_tx.keys()
