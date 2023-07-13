import faker
import factory.fuzzy
from factory.django import DjangoModelFactory

from apps.cryptocurrencies import models

fake = faker.Faker()


class NetworkFactory(DjangoModelFactory):
    class Meta:
        model = models.Network

    name = factory.Sequence(lambda n: "name#%d" % n)

    url = fake.unique.url()
    block_explorer_url = fake.unique.url()
    chain_id = factory.fuzzy.FuzzyInteger(low=1, high=10**2)

    active = True


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = models.Currency

    name = factory.Sequence(lambda n: "name#%d" % n)
    symbol = factory.Sequence(lambda n: "symbol#%d" % n)
    decimal_place = factory.fuzzy.FuzzyInteger(low=6, high=25)
    address = None

    network = factory.SubFactory(NetworkFactory)

    exchange_id = factory.Sequence(lambda n: "exchange_id#%d" % n)
    active = True

    class Params:
        is_stable_coin = factory.Trait(
            address=factory.Sequence(lambda n: "address#%d" % n),
        )


class ProviderFactory(DjangoModelFactory):
    class Meta:
        model = models.Provider

    address = factory.Sequence(lambda n: "address#%d" % n)
    network = factory.SubFactory(NetworkFactory)
