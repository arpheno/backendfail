import factory
from fiddles.factories import UserFactory, FiddleFileFactory
from ror.models import RailsFiddle


class RailsFiddleFactory(factory.DjangoModelFactory):
    class Meta:
        model = RailsFiddle

    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def files(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        self.save()
        obj = FiddleFileFactory(path="README.rdoc", fiddle=self)
        obj.save()
