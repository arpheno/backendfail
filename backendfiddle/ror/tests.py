import os
from time import sleep

import pytest
from django.test import Client
from fabric.operations import local

from dj.factories import DjangoFiddleFactory
from dj.models import DjangoFiddle



