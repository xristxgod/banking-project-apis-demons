from src.caches.ram import cached

from apps.cryptocurrencies.models import Currency


def generate_temp_wallet(currency: Currency):
    # TODO
    return {
        'address': '...',
        'private_key': '...',
    }


@cached(60 * 60)
def get_currency(pk: int) -> Currency:
    return Currency.objects.get(pk=pk)
