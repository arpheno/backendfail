import pytest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.test import Client
from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import re
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from dj.factories import DjangoFiddleFactory
from fiddles.factories import FiddleFactory, UserFactory
from fiddles.models import Fiddle

base_url = "http://localhost:8081"


@scenario('backendfail.feature', 'Viewing the main page')
def test_view_page():
    pass


@given('I have a web browser')
def browser():
    return webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        desired_capabilities=DesiredCapabilities.CHROME)


@when('I open the main page')
def view_main(browser, live_server):
    browser.maximize_window()
    browser.get(base_url)
    return browser


@then('the title should be backend.fail')
def page_viable(browser):
    assert "backend.fail" in browser.title
