from unittest import TestCase
from unittest.mock import Mock, patch
from src.node import btc
from src.services.v3.create_transaction import create_transaction
from src.utils import convert_time
from config import decimal, logger


class TestCreateTransactionsCase(TestCase):
    @patch('src.rpc.es_send.__send_msg_to_kibana')
    @patch('src.services.v3.sign_send_transaction.get_fee_for_transaction')
    @patch('src.node.NodeBTC.create_unsigned_transaction')
    @patch('src.node.RPCHost.is_trx_unspent')
    @patch('src.node.RPCHost.send')
    @patch('src.node.RPCHost.decode_transaction')
    @patch('src.services.v3.sign_send_transaction.formatted_tx')
    def test_create_transaction_with_admin_fee(
            self,
            formatted_tx: Mock,
            decode_transaction: Mock,
            send: Mock,
            is_trx_unspent: Mock,
            create_unsigned_transaction: Mock,
            get_fee_for_transaction: Mock,
            __send_msg_to_kibana: Mock
    ):
        __send_msg_to_kibana.return_value = None
        send.return_value = {
            'hex': 'd1787f67bbaa313f00e369c1961378bd2510d97bc451975b1a50f000c7459b21',
        }
        decode_transaction.return_value = {
            "hash": 'd1787f67bbaa313f00e369c1961378bd2510d97bc451975b1a50f000c7459b21',
            'size': 573,
            'vin': [{"address": 'bc1qnsupj8eqya02nm8v6tmk93zslu2e2z8chlmcej', "amount": '0.22067577'}],
            'vout': [
                {"address": "1CwajZFoCpAsQdHnDYK722T2VMfXWrNsLA", "amount": "0.00780000", "n": 0},
                {"address": "bc1qnsupj8eqya02nm8v6tmk93zslu2e2z8chlmcej", "amount": "0.21286861", "n": 1},
            ]
        }
        formatted_tx.return_value = {
            "time": 12314212,
            "datetime": convert_time(12314212),
            "transactionHash": 'd1787f67bbaa313f00e369c1961378bd2510d97bc451975b1a50f000c7459b21',
            "amount": '0.22067577',
            "fee": "0.00000716",
            "senders": [{"address": 'bc1qnsupj8eqya02nm8v6tmk93zslu2e2z8chlmcej', "amount": '0.22067577'}],
            "recipients": [
                {"address": "1CwajZFoCpAsQdHnDYK722T2VMfXWrNsLA", "amount": "0.00780000", "n": 0},
                {"address": "bc1qnsupj8eqya02nm8v6tmk93zslu2e2z8chlmcej", "amount": "0.21286861", "n": 1},
            ]
        }
        is_trx_unspent.return_value = True
        create_unsigned_transaction.return_value = ({'size': 119}, True)
        get_fee_for_transaction.return_value = (decimal.create_decimal(0.00001), decimal.create_decimal(0.0001))
        created_tx = create_transaction(
            [{'1CwajZFoCpAsQdHnDYK722T2VMfXWrNsLA': '0.00780000'}],
            'bc1qnsupj8eqya02nm8v6tmk93zslu2e2z8chlmcej'
        )

        logger.error(f'{created_tx}')

        assert isinstance(created_tx, dict)
        assert 'error' not in created_tx.keys()
        assert 'fee' in created_tx.keys()
        assert 'maxFeeRate' in created_tx.keys()

    @patch('src.node.RPCHost.decode_transaction')
    @patch('src.node.RPCHost.create_raw_transaction')
    def test_create_transaction_success(self, create_raw_transaction: Mock, mock_decode_transaction: Mock):
        create_raw_transaction.return_value = '0200000001ac00000000'
        mock_decode_transaction.return_value = {'txid': '123456789012345678901234567890123'}

        created_tx, is_created = btc.create_unsigned_transaction([], [])
        assert isinstance(created_tx, dict)
        assert 'txid' in created_tx.keys()
        assert 'createTxHex' in created_tx.keys()
        assert is_created is True

    @patch('src.node.RPCHost.decode_transaction')
    @patch('src.node.RPCHost.create_raw_transaction')
    def test_create_transaction_error(self, create_raw_transaction: Mock, mock_decode_transaction: Mock):
        create_raw_transaction.return_value = False
        mock_decode_transaction.return_value = {'error': 'error text'}

        created_tx, is_created = btc.create_unsigned_transaction([], [])

        assert isinstance(created_tx, dict)
        assert 'error' in created_tx.keys()
        assert is_created is False
