import pytest

from tests.factories import fake_stable_coin


# @pytest.mark.asyncio
def test_stable_coin_storage():
    from core.node import StableCoinStorage

    class FakeStableCoinObject:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    storage = StableCoinStorage()

    stable_coin_1 = FakeStableCoinObject(**fake_stable_coin()._asdict())
    stable_coin_2 = FakeStableCoinObject(**fake_stable_coin()._asdict())
    stable_coin_3 = FakeStableCoinObject(**fake_stable_coin()._asdict())

    storage.update({
        # key: address & symbol | value: contract obj
        (stable_coin_1.address, stable_coin_1.symbol): stable_coin_1,
        (stable_coin_2.address, stable_coin_2.symbol): stable_coin_2,
    })

    assert (
            storage[(stable_coin_1.address, stable_coin_1.symbol)] == stable_coin_1 and
            storage[stable_coin_1.address] == stable_coin_1 and
            storage[stable_coin_1.symbol] == stable_coin_1
    )

    assert (
            storage.get((stable_coin_2.address, stable_coin_2.symbol)) == stable_coin_2 and
            storage.get(stable_coin_2.address) == stable_coin_2 and
            storage.get(stable_coin_2.symbol) == stable_coin_2
    )

    with pytest.raises(KeyError) as e:
        _ = storage[stable_coin_3.address]
