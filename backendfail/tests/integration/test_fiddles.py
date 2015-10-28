import os
from time import sleep
import pytest
from django.test import Client
from fabric.operations import local
from dj.factories import DjangoFiddleFactory
from dj.models import DjangoFiddle
from fiddles.factories import UserFactory, FiddleFactory


@pytest.mark.django_db
def test_model_creation():
    obj = FiddleFactory.create()
    assert obj.fiddlefile_set.count() == 1
