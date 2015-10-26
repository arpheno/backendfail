import factory

from dj.models import DjangoFiddle


class DjangoFiddleFactory(factory.Factory):
    class Meta:
        model = DjangoFiddle

    name = factory.sequence(lambda x: "djangoname" + str(x))
