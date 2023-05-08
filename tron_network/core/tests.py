import pytest

from core.decorators import encode, decode


def test_encode_and_decode():
    value = 'test_value'

    class TempObjects:
        a = 'temp_a'
        b = 'temp_b'

    @encode(type=str, take='response')
    def temp_func_encode_response(temp_value: str):
        return temp_value

    @encode(values=['a', 'b'], type=object, take='request')
    def temp_func_encode_request(temp_object: TempObjects):
        return temp_object

    @decode(type=str, take='request')
    def temp_func_decode_request(temp_value: str):
        return temp_value

    @decode(values=['a', 'b'], type=dict, take='response')
    def temp_func_decode_response(temp_dict: dict):
        return temp_dict

    encode_value_str = temp_func_encode_response(temp_value=value)
    encode_value_object = temp_func_encode_request(temp_object=TempObjects())

    assert encode_value_str != value
    assert encode_value_object.a != TempObjects.a and encode_value_object.b != TempObjects.b




@pytest.mark.asyncio
async def test_async_encode_and_decode():
    pass
