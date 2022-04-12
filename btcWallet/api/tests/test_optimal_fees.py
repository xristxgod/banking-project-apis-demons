from unittest import TestCase
from unittest.mock import Mock, patch
from nose.tools import assert_dict_equal
from src.node import btc


class TestOptimalFeesCase(TestCase):
    @patch('src.node.RPCHost.get_btc_to_kb')
    def test_get_optimal_fees_success(self, get_btc_to_kb: Mock):
        get_btc_to_kb.return_value = 1000
        optimal_fees = btc.get_optimal_fees(1, 1, 1)
        assert_dict_equal(
            {
                'transfer': '1 input -> 1 output | Blocks 1', 'BTC/KB': '1000.00000000',
                'BTC/BYTE': '1.00000000',
                'SAT/KB': '100000000000.00000000',
                'SAT/BYTE': '100000000.00000000',
                'bytes': '225',
                'satoshi': '22500000000',
                'btc': '225.00000000'
            },
            optimal_fees
        )
