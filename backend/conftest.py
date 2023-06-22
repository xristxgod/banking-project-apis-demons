# pylint: disable
import pytest


# noinspection PyUnusedLocal,PyProtectedMember
@pytest.fixture(autouse=True, scope="session")
def django_test_environment(django_test_environment):
    from django.apps import apps

    get_models = apps.get_models

    for m in [m for m in get_models()]:
        if not m._meta.managed and not m._meta.abstract:
            m._meta.managed = True
