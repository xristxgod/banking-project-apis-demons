import faker
import factory.fuzzy
from factory.django import DjangoModelFactory

from apps.cryptocurrencies import models

fake = faker.Faker()


class NetworkFactory(DjangoModelFactory):
    class Meta:
        model = models.Network

    name = factory.Sequence(lambda n: "name#%d" % n)
    chain_id = factory.fuzzy.FuzzyInteger(low=1, high=10**2)
    url = fake.unique.url()
    active = True


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = models.Currency

    name = factory.Sequence(lambda n: "name#%d" % n)
    symbol = factory.Sequence(lambda n: "symbol#%d" % n)
    decimal_place = factory.fuzzy.FuzzyInteger(low=6, high=25)
    address = None
    network = factory.SubFactory(NetworkFactory)
    active = True

    class Params:
        stable_coin = factory.Trait(
            address=factory.Sequence(lambda n: "address#%d" % n),
        )


class ProviderFactory(DjangoModelFactory):
    class Meta:
        model = models.Provider

    address = None
    network = factory.Sequence(lambda n: "address#%d" % n)
