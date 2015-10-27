from django.core.urlresolvers import reverse_lazy
from django.test import Client
from pytest_bdd import scenario, given, when, then

from fiddles.factories import FiddleFactory


@scenario('fiddlefiles.feature', 'Viewing files without login')
def test_view():
    pass

@scenario('fiddlefiles.feature', 'Editing files without login')
def test_edit():
    pass

@given("I'm not logged in")
def client():
    return Client()

@given("There is a file")
def fiddlefile(db):
    return FiddleFactory().fiddlefile_set.first()
@when('I look at the file')
def get_file(fiddlefile, client):
    client.response= client.get(
        reverse_lazy('file-view',
                     kwargs={
                         "pk":fiddlefile.fiddle.id,
                         "path":fiddlefile.path
                             }
                     )
    )
@then('I should not be able to edit it')
def file_not_editable(client):
    assert "editor.setReadOnly(true)" in client.response.content
@when('I try to edit the file')
def get_edit_view(fiddlefile, client):
    client.response= client.get(
        reverse_lazy('file-edit',
                     kwargs={
                         "pk":fiddlefile.fiddle.id,
                         "path":fiddlefile.path
                     }
                     )
    )
@then('I should be redirected to the login')
def redirected_login(client):
    assert "/login/github/" in client.response.url
