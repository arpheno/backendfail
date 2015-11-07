import factory

from dj.models import DjangoFiddle
from fiddles.factories import UserFactory, FiddleFileFactory


class DjangoFiddleFactory(factory.DjangoModelFactory):
    class Meta:
        model = DjangoFiddle
    owner = factory.SubFactory(UserFactory)

