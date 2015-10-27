import factory
from django.contrib.auth.models import User

from fiddles.models import Fiddle, FiddleFile

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    email = 'admin@admin.com'
    username = 'admin'
    password = factory.PostGenerationMethodCall('set_password', 'adm1n')

    is_superuser = True
    is_staff = True
    is_active = True
class FiddleFileFactory(factory.Factory):
    class Meta:
        model = FiddleFile
    content = ""
    path="your mom"

class FiddleFactory(factory.Factory):
    class Meta:
        model = Fiddle
    owner = factory.SubFactory(UserFactory)
    @factory.post_generation
    def files(self,create,extracted,**kwargs):
        if not create:
            # Simple build, do nothing.
            return
        self.save()
        obj = FiddleFileFactory(path="app/templates/app",fiddle=self)
        obj.save()

