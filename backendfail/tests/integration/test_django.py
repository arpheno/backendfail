import os
from time import sleep
import pytest
from django.test import Client
from fabric.operations import local
from dj.factories import DjangoFiddleFactory
from dj.models import DjangoFiddle
from fiddles.factories import UserFactory
from settings.basic import BASE_DIR


@pytest.mark.django_db
def test_django_creation():
    obj = DjangoFiddleFactory.create()
    obj.save()
    assert obj.fiddlefile_set.count() > 0


@pytest.mark.django_db
def test_django_write_files():
    obj = DjangoFiddleFactory()
    obj.save()
    assert os.path.exists(obj.root)
    assert os.path.exists(os.path.join(obj.root, 'app'))
    assert os.path.exists(os.path.join(obj.root, 'app', '__init__.py'))


@pytest.mark.django_db
def test_create_django():
    cli = Client()
    usr = UserFactory()
    cli.login(user=usr)
    response = cli.get("/new/DjangoFiddle/")
    assert DjangoFiddle.objects.count() == 1
