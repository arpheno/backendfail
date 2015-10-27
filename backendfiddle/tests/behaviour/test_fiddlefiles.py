from django.core.urlresolvers import reverse_lazy
from django.test import Client
from pytest_bdd import scenario, given, when, then

from fiddles.factories import FiddleFactory


@scenario('fiddlefiles.feature', 'Viewing files without login')
def test_publish():
    pass


@given("I'm not logged in")
def anon_client():
    return Client()

@given("There is a file")
def fiddlefile(db):
    return FiddleFactory().fiddlefile_set.first()
@when('I look at the file')
def get_file(fiddlefile, anon_client):
    anon_client.response= anon_client.get(
        reverse_lazy('file-view',
                     kwargs={
                         "pk":fiddlefile.fiddle.id,
                         "path":fiddlefile.path
                             }
                     )
    )
@then('I should not be able to edit it')
def file_not_editable(anon_client):
    assert "editor.setReadOnly(true)" in anon_client.response.content
