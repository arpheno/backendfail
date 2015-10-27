import pytest
from django.core.urlresolvers import reverse_lazy
from django.test import Client
from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import re

from fiddles.factories import FiddleFactory, UserFactory
from fiddles.models import Fiddle


@scenario('fiddlefiles.feature', 'Viewing files without login')
def test_view_anon():
    pass

@scenario('fiddlefiles.feature', 'Editing files without login')
def test_edit_anon():
    pass
@scenario('fiddlefiles.feature', 'Creating fiddles without login')
def test_edit_create_anon():
    pass
@scenario('fiddlefiles.feature', 'Creating fiddles with login')
def test_edit_create():
    pass

@given("")
@given(re(r"I'm logged in as (?P<user>.*)"))
@pytest.mark.django_db
def myclient(user,client,admin_client):
    if user =="no one":
        return client
    if user == "an admin":
        return admin_client
    obj = UserFactory(username=user)
    client.login(user=obj)
    return client

@given("There is a file")
def fiddlefile(db):
    return FiddleFactory().fiddlefile_set.first()
@given("There is no fiddle")
def purge_fiddle(db):
    Fiddle.objects.all().delete()
    assert Fiddle.objects.count()==0
@when('I look at the file')
def get_file(fiddlefile, myclient):
    myclient.response= myclient.get(
        reverse_lazy('file-view',
                     kwargs={
                         "pk":fiddlefile.fiddle.id,
                         "path":fiddlefile.path
                             }
                     )
    )
@then('I should not be able to edit it')
def file_not_editable(myclient):
    assert "editor.setReadOnly(true)" in myclient.response.content
@when('I try to edit the file')
def get_edit_view(fiddlefile, myclient):
    myclient.response= myclient.get(
        reverse_lazy('file-edit',
                     kwargs={
                         "pk":fiddlefile.fiddle.id,
                         "path":fiddlefile.path
                     }
                     )
    )
@then('I should be redirected to the login')
def redirected_login(myclient):
    assert "/login/github/" in myclient.response.url
@when('I try to create a fiddle')
def get_create_view(myclient):
    myclient.response= myclient.get(
        reverse_lazy('fiddle-create',kwargs={"class":"Fiddle"})
    )
@then('A fiddle should be created')
def fiddle_created(myclient):
    assert Fiddle.objects.count()==1
