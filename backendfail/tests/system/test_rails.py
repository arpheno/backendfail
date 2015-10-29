from time import sleep
import pytest
from django.core.urlresolvers import reverse_lazy
from django.test import Client
from fabric.operations import local
from dj.factories import DjangoFiddleFactory
from dj.models import DjangoFiddle
from ror.factories import RailsFiddleFactory
from ror.models import RailsFiddle


@pytest.mark.docker
@pytest.mark.django_db
def test_django_launch_unit():
    assert RailsFiddle.objects.count() == 0
    obj = RailsFiddleFactory.create()
    obj.save()
    obj._hash()
    obj._write_files()
    obj._launch()
    sleep(15)
    try:
        assert local('curl localhost:' + str(obj.port), capture=True).return_code == 0
    except:
        obj.cleanup()
