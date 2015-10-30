import pytest
import time
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.test import Client
from fabric.operations import local
from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import re
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

from dj.factories import DjangoFiddleFactory
from fiddles.factories import FiddleFactory, UserFactory
from fiddles.models import Fiddle



@pytest.mark.docker
@scenario('backendfail.feature', 'Viewing the main page')
def test_view_page():
    pass


@pytest.mark.docker
@scenario('backendfail.feature', 'Redirection to facebook')
def test_login_facebook():
    pass


@pytest.mark.docker
@scenario('backendfail.feature', 'Redirection to backendfail')
def test_login_facebook_redirect_back():
    pass


@pytest.mark.docker
# @scenario('backendfail.feature', 'Creating a new fail')
# def test_create_fail():
#     pass

@given('I have a web browser')
def browser():
    return webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        desired_capabilities=DesiredCapabilities.CHROME)


@when('I open the main page')
def view_main(browser):
    assert "backend.fail" in local("curl http://localhost:9000/", capture=True)
    browser.maximize_window()
    browser.get("http://localhost:9000/")
    return browser


@when('I try to login via facebook')
def facebook_attempt(browser):
    browser.delete_all_cookies()
    browser.get("http://localhost:9000/login/facebook/")


@when('I succeed at logging in via facebook')
def facebook_succeed(browser):
    try:
        elem = browser.find_element_by_id("email")
        elem.send_keys("alfred_jgwywzx_batman@tfbnw.net")
        elem = browser.find_element_by_id("pass")
        elem.send_keys("phracking")
        elem.send_keys(Keys.RETURN)
        elem = browser.find_element_by_name("login")
        elem.click()
    except:
        pass


@then(re(r'I should be redirected to (?P<destination>.*)'))
def redirected(browser, destination):
    assert destination in browser.current_url
@then('the title should be backend.fail')
def page_viable(browser):
    assert "backend.fail" in browser.title
