"""
This test checks the operability of sending messages to Kibana.
# Check everything
python -m unittest test_send_es.TestSendToKibana
# Send a test message to the Kibana log.
python -m unittest test_send_es.TestSendToKibana.test_send_to_kibana_msg
 # Send a test error message to the Kibana log.
python -m unittest test_send_es.TestSendToKibana.test_send_to_kibana_ex
"""
import unittest

from src_1.utils.es_send import send_msg_to_kibana, send_exception_to_kibana

class TestSendToKibana(unittest.IsolatedAsyncioTestCase):

    async def test_send_to_kibana_msg(self):
        self.assertTrue(await send_msg_to_kibana("Test Message"))

    async def test_send_to_kibana_ex(self):
        try:
            raise Exception()
        except Exception as error:
            self.assertTrue(await send_exception_to_kibana(error, "Test Exception"))
