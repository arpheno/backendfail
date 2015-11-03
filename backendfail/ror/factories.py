import factory
from fiddles.factories import UserFactory, FiddleFileFactory
from ror.models import RailsFiddle


class RailsFiddleFactory(factory.DjangoModelFactory):
    class Meta:
        model = RailsFiddle

    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def files(self, create, extracted, **kwargs):
        self.save()
        obj = FiddleFileFactory(path="README.rdoc", fiddle=self)
        obj.save()
