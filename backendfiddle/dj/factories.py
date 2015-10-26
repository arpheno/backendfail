import factory

from dj.models import DjangoFiddle
from fiddles.factories import UserFactory


class DjangoFiddleFactory(factory.Factory):
    class Meta:
        model = DjangoFiddle
    owner = factory.SubFactory(UserFactory)
