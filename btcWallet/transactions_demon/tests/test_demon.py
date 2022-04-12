from unittest import TestCase
from unittest.mock import Mock, patch
from src.external_data.database import DB


class MockedDB:
    def cursor(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs):
        return []

    def fetchone(self, *args, **kwargs):
        return []

    def fetchall(self, *args, **kwargs):
        return []

    def close(self, *args, **kwargs):
        return None


class TestDemon(TestCase):
    @patch('src.external_data.es_send.__send_msg_to_kibana')
    @patch('psycopg2.connect')
    @patch('tests.test_demon.MockedDB.cursor')
    @patch('tests.test_demon.MockedDB.fetchone')
    @patch('tests.test_demon.MockedDB.fetchall')
    def test_get_addresses(
            self,
            fetchall: Mock,
            fetchone: Mock,
            cursor: Mock,
            connect: Mock,
            __send_msg_to_kibana: Mock,
    ):
        connect.return_value = MockedDB()
        cursor.return_value = MockedDB()
        fetchall.return_value = ['f', 'f']
        fetchone.return_value = ['f']
        __send_msg_to_kibana.return_value = None

        addresses = DB().get_addresses()
        assert isinstance(addresses, list)
        assert len(addresses) > 0

        tx_hash = DB.get_all_transactions_hash()
        assert tx_hash is not None
        assert isinstance(tx_hash, list)
        if len(tx_hash) > 0:
            tx = DB.get_transaction_by_hash(transaction_hash=tx_hash[0])
            assert isinstance(tx, list)
