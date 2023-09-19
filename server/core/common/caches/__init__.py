from .ram import cached as ram_cached
from .redis import cached as redis_cached

__all__ = (
    'ram_cached',
    'redis_cached',
)
