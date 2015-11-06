import pytest
from django.core.urlresolvers import reverse_lazy
from django.test import Client
from dj.factories import DjangoFiddleFactory
from dj.models import DjangoFiddle


@pytest.mark.system
@pytest.mark.django_db
def test_django_launch_functional():
    assert DjangoFiddle.objects.count() == 0
    obj = DjangoFiddleFactory.create()
    obj.save()
    c = Client()
    response = c.get(reverse_lazy('result', kwargs={"pk": obj.id, "path": ""}))
    assert response.status_code == 200


@pytest.mark.system
@pytest.mark.django_db
def test_django_launch_twice():
    obj = DjangoFiddleFactory.create()
    obj.save()
    c = Client()
    response = c.get(reverse_lazy('result', kwargs={"pk": obj.id, "path": ""}))
    assert response.status_code == 200
    response = c.get(reverse_lazy('result', kwargs={"pk": obj.id, "path": ""}))
    assert response.status_code == 200
@pytest.mark.system
@pytest.mark.django_db
def test_skeleton():
    obj = DjangoFiddleFactory.create()
    obj.save()
    c = Client()
    response = c.get(reverse_lazy('result', kwargs={"pk": obj.id, "path": ""}))
    assert response.status_code == 200
    response = c.get(reverse_lazy('result', kwargs={"pk": obj.id, "path": "blogs/new/"}))
    assert response.status_code == 200
    response = c.post(reverse_lazy('result', kwargs={"pk": obj.id, "path": "blogs/new/"}),{"name":"peter"})
    assert response.status_code == 302
    response = c.get(reverse_lazy('result', kwargs={"pk": obj.id, "path": "blogs"}))
    assert "peter" in response.content
