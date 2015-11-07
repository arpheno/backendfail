import pytest
from dj.factories import DjangoFiddleFactory
from dj.models import DjangoFiddle
from fiddles.helpers import public_port, copy_object, rewrite_redirect
from fiddles.models import Fiddle


@pytest.mark.unit
def test_public_port():
    container = {"Ports": [{"PublicPort": 8000}, {"PublicPort": 9000}]}
    assert public_port(container) is 8000


class FakeObject:
    pass


@pytest.mark.unit
def test_rewrite_redirect():
    response = FakeObject()
    response._headers = {"location": ('Location', "http://localhost:9000/hello")}
    request = FakeObject()
    def uri():
        return "http://localhost:9000/12/result//asd"
    request.build_absolute_uri = uri
    expected = ('Location', "http://localhost:9000/12/result//hello/")
    result = rewrite_redirect(response, request)
    assert expected == result


@pytest.mark.integration
@pytest.mark.django_db
def test_copy_fiddle():
    fiddle = DjangoFiddleFactory()
    other_fiddle = copy_object(DjangoFiddle.objects.get(id=fiddle.id))
    assert fiddle.id
    assert other_fiddle.id
    assert fiddle.id != other_fiddle.id
    assert Fiddle.objects.count() == 2
