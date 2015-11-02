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
def test_rails_launch_functional():
    assert RailsFiddle.objects.count() == 0
    obj = RailsFiddleFactory.create()
    obj.save()
    c = Client()
    response = c.get(reverse_lazy('result', kwargs={"pk": obj.id, "url": ""}))
    assert response.status_code == 200
