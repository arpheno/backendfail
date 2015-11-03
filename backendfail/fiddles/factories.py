import factory
from django.contrib.auth.models import User

from fiddles.models import Fiddle, FiddleFile

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    email = 'admin@admin.com'
    username = factory.sequence(lambda x: 'admine' + str(x))
    password = factory.PostGenerationMethodCall('set_password', 'adm1n')

    is_superuser = True
    is_staff = True
    is_active = True
class FiddleFileFactory(factory.DjangoModelFactory):
    class Meta:
        model = FiddleFile
        django_get_or_create =['fiddle','path']
    content = ""
    path="your mom"


