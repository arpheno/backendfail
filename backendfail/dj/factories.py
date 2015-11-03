import factory

from dj.models import DjangoFiddle
from fiddles.factories import UserFactory, FiddleFileFactory


class DjangoFiddleFactory(factory.DjangoModelFactory):
    class Meta:
        model = DjangoFiddle
    owner = factory.SubFactory(UserFactory)
    @factory.post_generation
    def files(self,create,extracted,**kwargs):
        self.save()
        obj = FiddleFileFactory(path="app/templates/app/app.html",fiddle=self)
        obj.save()
        obj = FiddleFileFactory(path="app/__init__.py",fiddle=self)
        obj.save()
