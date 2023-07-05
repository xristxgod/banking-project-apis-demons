from datetime import datetime


class TestRamCached:
    """ src.caches.ram.Cached """
    def test_cached(self):
        from src.caches.ram import cached

        @cached(12)
        def temp_func(a: int, b: int) -> int:
            return a + b

        result1 = temp_func(1, 2)
        assert len(cached._storage.keys()) == 1
        key1 = list(cached._storage.keys())[0]
        assert cached._storage[key1][0] == result1
        assert isinstance(cached._storage[key1][1], datetime)

        result2 = temp_func(a=1, b=2)
        assert len(cached._storage.keys()) == 1
        key2 = list(cached._storage.keys())[0]
        assert cached._storage[key2][0] == result2
        assert isinstance(cached._storage[key2][1], datetime)

        result3 = temp_func(1, b=2)
        assert len(cached._storage.keys()) == 1
        key3 = list(cached._storage.keys())[0]
        assert cached._storage[key3][0] == result3
        assert isinstance(cached._storage[key3][1], datetime)

        assert key1 == key2 == key3
        assert result1 == result2 == result3

        result4 = temp_func(2, 5)
        assert len(cached._storage.keys()) == 2
        key4 = list(cached._storage.keys())[1]
        assert cached._storage[key4][0] == result4
        assert isinstance(cached._storage[key4][1], datetime)

        assert key4 not in [key1, key2, key3]
        assert result4 not in [result1, result2, result3]
