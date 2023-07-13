import factory.fuzzy
import faker
from factory.django import DjangoModelFactory

from apps.users import models


class UserFactory(DjangoModelFactory):
    class Meta:
        model = models.User

    id = factory.fuzzy.FuzzyInteger(low=1, high=10**3)
    username = factory.Sequence(lambda n: "username#%d" % n)
