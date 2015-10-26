import factory
from fiddles.models import Fiddle, FiddleFile


class FiddleFileFactory(factory.Factory):
    class Meta:
        model = FiddleFile
    file = factory.django.FileField(data = "fart")

class FiddleFactory(factory.Factory):
    class Meta:
        model = Fiddle
    name = factory.sequence(lambda x: "default_name_"+ str(x))
    @factory.post_generation
    def files(self,create,extracted,**kwargs):
        if not create:
            # Simple build, do nothing.
            return
        self.save()
        obj = FiddleFileFactory(fiddle=self)
        obj.save()

