import pytest
from django.core.urlresolvers import reverse_lazy
from ror.factories import RailsFiddleFactory


@pytest.mark.system
@pytest.mark.django_db
def test_rails_launch_functional(client):
    obj = RailsFiddleFactory.create()
    obj.save()
    response = client.get(reverse_lazy('result', kwargs={"pk": obj.id, "path": ""}))
    assert response.status_code == 200
