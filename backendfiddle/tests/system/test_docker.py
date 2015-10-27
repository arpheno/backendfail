from time import sleep

import pytest
from django.core.urlresolvers import reverse_lazy
from django.test import Client
from fabric.operations import local

from dj.factories import DjangoFiddleFactory
from dj.models import DjangoFiddle


@pytest.mark.docker
@pytest.mark.django_db
def test_django_launch_unit():
    assert DjangoFiddle.objects.count() == 0
    obj = DjangoFiddleFactory.create()
    obj.save()
    obj._hash()
    obj._write_files()
    obj._launch()
    sleep(15)
    try:
        assert local('curl localhost:'+str(obj.port),capture=True).return_code == 0
        try:
            obj._stop()
            obj._delete_files()
        except:
            pass
    except:
        try:
            obj.cleanup()
            obj._delete_files()
        except:
            pass
        raise
@pytest.mark.docker
@pytest.mark.django_db
def test_django_launch_functional():
    assert DjangoFiddle.objects.count() == 0
    obj = DjangoFiddleFactory.create()
    obj.save()
    c = Client()
    response = c.get(reverse_lazy('result',kwargs={"pk":obj.id,"url":""}))
    obj=DjangoFiddle.objects.get(pk=obj.id)
    try:
        assert response.status_code==200
        try:
            obj._stop()
            obj._remove()
            obj._delete_files()
        except:
            pass
    except:
        try:
            obj._stop()
            obj._remove()
            obj._delete_files()
        except:
            pass
        raise
