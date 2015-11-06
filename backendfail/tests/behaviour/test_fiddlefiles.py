import pytest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.test import Client
from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import re
from dj.factories import DjangoFiddleFactory
from fiddles.factories import UserFactory
from fiddles.models import Fiddle



@pytest.mark.integration
@scenario('fiddlefiles.feature', 'Creating files with login')
def test_creating_files_with_login():
    """Creating files with login."""


@pytest.mark.integration
@pytest.mark.django_db
@scenario('fiddlefiles.feature', 'Renaming files with login')
def test_renaming_files_with_login():
    """Creating files with login."""


@pytest.mark.django_db
@scenario('fiddlefiles.feature', 'Deleting files with login')
def test_deleting_files_with_login():
    """Creating files with login."""


@scenario('fiddlefiles.feature', 'Viewing files without login')
def test_view_anon():
    pass



@pytest.mark.integration
@scenario('fiddlefiles.feature', 'Editing files without login')
def test_edit_anon():
    pass



@pytest.mark.integration
@scenario('fiddlefiles.feature', 'Editing files with login')
def test_edit():
    pass



@pytest.mark.integration
@scenario('fiddlefiles.feature', 'Viewing edit mode files with login')
def test_view_edit():
    pass



@pytest.mark.integration
@scenario('fiddlefiles.feature', 'Creating fiddles without login')
def test_edit_create_anon():
    pass


@pytest.mark.integration
@scenario('fiddlefiles.feature', 'Creating fiddles with login')
def test_edit_create():
    pass


@pytest.mark.integration
@scenario('fiddlefiles.feature', 'Viewing editing files of others')
def test_edit_copy_view():
    pass


@pytest.mark.integration
@scenario('fiddlefiles.feature', 'Editing files of others')
def test_edit_copy():
    pass


@given(re(r"I'm logged in as (?P<user>.*)"))
def myclient(user, client, admin_client, db):
    if user == "no one":
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
def obtain(fiddlefile, user):
    fiddlefile.fiddle.owner = User.objects.get(username=user)
    fiddlefile.fiddle.save()


@given("I don't own the file")
def dontown(fiddlefile, user):
    pass


@given('I own the fiddle')
def i_own_the_fiddle(fiddle, user):
    """I own the fiddle."""
    fiddle.owner = User.objects.get(username=user)
    fiddle.save()


@given('There is a fiddle')
def fiddle(db):
    """There is a fiddle."""
    return DjangoFiddleFactory()


@given("There is no fiddle")
def purge_fiddle(db):
    Fiddle.objects.all().delete()
    assert Fiddle.objects.count() == 0


@when('I look at the file')
def get_file(fiddlefile, myclient):
    myclient.response = myclient.get(
        reverse_lazy('file-view',
                     kwargs={
                         "pk": fiddlefile.fiddle.id,
                         "path": fiddlefile.path
                     }
                     )
    )


@when('I try to access edit the file')
def get_edit_view(fiddlefile, myclient):
    info = {
        "pk": fiddlefile.fiddle.id,
        "path": fiddlefile.path
    }
    url = reverse_lazy('file-edit', kwargs=info)
    myclient.response = myclient.get(url)


@when('I try to edit the file')
def post_edit_view(fiddlefile, myclient):
    myclient.response = myclient.post(
        reverse_lazy('file-edit',
                     kwargs={
                         "pk": fiddlefile.fiddle.id,
                         "path": fiddlefile.path
                     }
                     ), {"content": "edited"}
    )


@when('I try to create a fiddle')
def get_create_view(myclient):
    myclient.response = myclient.get(
        reverse_lazy('fiddle-create', kwargs={"class": "DjangoFiddle"})
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
    assert Fiddle.objects.count() == 1


@then('The fiddle should be copied')
def copy_fiddle():
    assert Fiddle.objects.count() == 2


@then('I should own the copy')
def own_file(user):
    usr = User.objects.get(username=user)
    assert any(fiddle.owner == usr for fiddle in Fiddle.objects.all())


@then('I should be redirected to the file')
def redirect_file(myclient):
    assert myclient.response.url


@then('Permission should be denied')
def redirect_file(myclient):
    assert myclient.response.status_code == 403


@then('It should be edited')
def file_edited(fiddlefile):
    fiddlefile.refresh_from_db()
    assert fiddlefile.content == "edited"


@when('I try to create a fiddlefile')
def i_try_to_create_a_fiddlefile(fiddle, myclient):
    """I try to create a fiddlefile."""
    myclient.response = myclient.post(
        reverse_lazy('file-create',
                     kwargs={
                         "pk": fiddle.id,
                     }
                     ), {"path": "example", "content": ""}
    )


@when('I try to rename the file')
def i_try_to_rename_the_file(fiddlefile, myclient):
    """I try to create a fiddlefile."""
    myclient.response = myclient.post(
        reverse_lazy('file-rename',
                     kwargs={
                         "pk": fiddlefile.fiddle.id,
                         "path": fiddlefile.path,

                     }
                     ), {"path": "example"}
    )


@when('I try to delete the file')
def i_try_to_rename_the_file(fiddlefile, myclient):
    """I try to create a fiddlefile."""
    myclient.response = myclient.post(
        reverse_lazy('file-delete',
                     kwargs={
                         "pk": fiddlefile.fiddle.id,
                         "path": fiddlefile.path,
                     }
                     ), {"path": "example"}
    )


@then('The file should be deleted')
def the_file_should_be_deleted(fiddlefile):
    """A file should be created."""
    assert not fiddlefile in fiddlefile.fiddle.fiddlefile_set.all()


@then('The file should be renamed')
def the_file_should_be_renamed(fiddlefile):
    """A file should be created."""
    fiddlefile.refresh_from_db()
    assert fiddlefile.path == "example"


@then('A file should be created')
def a_file_should_be_created(fiddle):
    """A file should be created."""
    fiddle.refresh_from_db()
    assert "example" in [file.path for file in fiddle.fiddlefile_set.all()]
