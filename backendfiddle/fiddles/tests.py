import os
from time import sleep

import pytest
from django.test import TestCase

# Create your tests here.
from fabric.operations import local

from fiddles.factories import FiddleFactory, DjangoFiddleFactory


@pytest.mark.django_db
def test_model_creation():
    obj = FiddleFactory.create()
    assert obj.fiddlefile_set.count()==1
@pytest.mark.django_db
def test_django_creation():
    obj = DjangoFiddleFactory.create()
    obj.save()
    assert obj.fiddlefile_set.count()>0
@pytest.mark.django_db
def test_django_write_files():
    obj = DjangoFiddleFactory.create()
    obj.save()
    obj._hash()
    obj._write_files()
    root = os.path.join("containers",obj.hash)
    assert os.path.exists(root)
    assert os.path.exists(os.path.join(root,'app'))
    assert os.path.exists(os.path.join(root,'app','__init__.py'))
    obj._delete_files()
    assert not os.path.exists(root)

@pytest.mark.django_db
def test_django_launch():
    obj = DjangoFiddleFactory.create()
    obj.save()
    obj._hash()
    obj._write_files()
    obj._launch()
    sleep(8)
    try:
        assert local('curl localhost:'+str(obj.port),capture=True).return_code == 0
        obj.cleanup()
    except:
        obj.cleanup()
        raise
