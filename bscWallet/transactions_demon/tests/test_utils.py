from unittest import IsolatedAsyncioTestCase
from src.utils import convert_time


class TestProjectMethods(IsolatedAsyncioTestCase):
    async def test_convert_time(self):
        assert convert_time(1646810906) == "09-03-2022 10:28:26"
        assert convert_time(1643682141) == "01-02-2022 05:22:21"
