import os
from time import sleep
import pytest
from django.test import TestCase, Client
# Create your tests here.
from fabric.operations import local
from fiddles.factories import FiddleFactory


@pytest.mark.django_db
def test_model_creation():
    obj = FiddleFactory.create()
    assert obj.fiddlefile_set.count() == 1
