import pytest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.test import Client
from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import re

from dj.factories import DjangoFiddleFactory
from fiddles.factories import FiddleFactory, UserFactory
from fiddles.models import Fiddle


@scenario('fiddlefiles.feature', 'Viewing files without login')
def test_view_anon():
    pass

@scenario('fiddlefiles.feature', 'Editing files without login')
def test_edit_anon():
    pass
@scenario('fiddlefiles.feature', 'Editing files with login')
def test_edit():
    pass
@scenario('fiddlefiles.feature', 'Viewing edit mode files with login')
def test_view_edit():
    pass
@scenario('fiddlefiles.feature', 'Creating fiddles without login')
def test_edit_create_anon():
    pass
@scenario('fiddlefiles.feature', 'Creating fiddles with login')
def test_edit_create():
    pass
@scenario('fiddlefiles.feature', 'Viewing editing files of others')
def test_edit_copy_view():
    pass
@scenario('fiddlefiles.feature', 'Editing files of others')
def test_edit_copy():
    pass

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
    return DjangoFiddleFactory().fiddlefile_set.first()
@given("I own the file")
def obtain(fiddlefile,user):
    fiddlefile.fiddle.owner=User.objects.get(username=user)
    fiddlefile.fiddle.save()
@given("I don't own the file")
def dontown(fiddlefile,user):
    pass
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
@when('I try to access edit the file')
def get_edit_view(fiddlefile, myclient):
    info={
        "pk":fiddlefile.fiddle.id,
        "path":fiddlefile.path
    }
    url = reverse_lazy('file-edit',kwargs=info)
    myclient.response= myclient.get(url)
@when('I try to edit the file')
def post_edit_view(fiddlefile, myclient):
    myclient.response= myclient.post(
        reverse_lazy('file-edit',
                     kwargs={
                         "pk":fiddlefile.fiddle.id,
                         "path":fiddlefile.path
                     }
                     ),{"content":"edited"}
    )
@when('I try to create a fiddle')
def get_create_view(myclient):
    myclient.response= myclient.get(
        reverse_lazy('fiddle-create',kwargs={"class":"DjangoFiddle"})
    )

@then('I should not be able to edit it')
def file_not_editable(myclient):
    assert "editor.setReadOnly(true)" in myclient.response.content
@then('I should be redirected to the login')
def redirected_login(myclient):
    assert "/login/github/" in myclient.response.url
@then('I should be able to view it')
def viewable(myclient):
    assert myclient.response.status_code == 200
@then('A fiddle should be created')
def fiddle_created(myclient):
    assert Fiddle.objects.count()==1
@then('The fiddle should be copied')
def copy_fiddle():
    assert Fiddle.objects.count() == 2
@then('I should own the copy')
def own_file(user):
    usr=User.objects.get(username=user)
    assert any(fiddle.owner==usr for fiddle in Fiddle.objects.all())
@then('I should be redirected to the file')
def redirect_file(myclient):
    assert myclient.response.url
@then('Permission should be denied')
def redirect_file(myclient):
    assert myclient.response.status_code == 403
@then('It should be edited')
def file_edited(fiddlefile):
    fiddlefile.refresh_from_db()
    assert fiddlefile.content =="edited"
