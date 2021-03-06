import hashlib
import os
from contextlib import contextmanager

import datetime
from django.views.decorators.cache import cache_page
from settings.basic import BASE_DIR
from django.contrib.auth.decorators import login_required
from docker.utils import create_host_config
from fabric.operations import local


class DoesNotExist(Exception):
    pass


def get_container_by_name(client, name):
    """
    Well it's kind of obvious what this function does.

    :param client: An instance of a docker api client
    :param name: The name of the container in question
    :return: If a container by that name exists, return its dict. Otherwise raise
    """
    try:
        return [c for c in client.containers(all=True) if "/" + name in c["Names"]][0]
    except IndexError:
        raise DoesNotExist("This container does not exist")


def public_port(container):
    """
    Gets the public facing port for a given container

    :param container: dict describing a container. Can be obtained from the dockerclient
    :return: int public port
    """
    return container["Ports"][0]["PublicPort"]


def build_container_config(internal_port, docker_image, startup_command):
    EXTERNAL_ROOT, INTERNAL_ROOT = '/var/containers/', '/usr/src/app'
    hash = hashlib.md5(str(datetime.datetime.now())).hexdigest()
    host_settings = {
        "port_bindings": {int(internal_port): None},
        "binds"        : [EXTERNAL_ROOT + hash + ':' + INTERNAL_ROOT]
    }
    host_config = create_host_config(**host_settings)
    return {
               "image"      : docker_image,
               "ports"      : [int(internal_port)],
               "volumes"    : [INTERNAL_ROOT],
               "working_dir": INTERNAL_ROOT,
               "command"    : startup_command,
               "host_config": host_config,
               "detach"     : True
           }, hash


@contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        pass


def write_file_to_disk(path, content):
    """
    :param path: Absolute filepath
    :param content: Content of the file
    :return:
    """
    import os
    dirpath = os.path.join(os.path.join(os.path.split(path)[0]))
    with suppress(OSError):
        os.makedirs(dirpath)
    with open(path, 'w') as file:
        file.write(content)


def read_files_from_disc(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            path = os.path.join(BASE_DIR, root, name)
            if path.startswith(directory, ):
                path = path.replace(directory, '', 1)
            with open(os.path.join(root, name)) as source:
                yield path, source.read()


def copy_object(original):
    fiddle = original
    fiddle.id, fiddle.pk = None, None
    fiddle.save()
    return fiddle


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class CacheMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(CacheMixin, cls).as_view(**initkwargs)
        return cache_page(60 * 15)(view)


def rewrite_redirect(response, request):
    """ Oh god, the aweful."""
    location = response._headers["location"][1]
    location = location[location.find("//") + 3:]
    path = location[location.find("/"):]
    base = request.build_absolute_uri()
    base = base[:base.find("t//") + 2]
    return 'Location', base + path + "/"
