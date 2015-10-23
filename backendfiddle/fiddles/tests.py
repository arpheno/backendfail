import pytest
from django.test import TestCase

# Create your tests here.
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

