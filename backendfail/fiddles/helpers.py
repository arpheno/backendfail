import os
from contextlib import contextmanager
from docker.utils import create_host_config

from settings.basic import BASE_DIR


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


def build_container_config(fiddle):
    EXTERNAL_ROOT, INTERNAL_ROOT = '/var/containers/', '/usr/src/app'
    host_settings = {
        "port_bindings": {int(fiddle.internal_port): None},
        "binds"        : [EXTERNAL_ROOT + fiddle.hash + ':' + INTERNAL_ROOT]
    }
    host_config = create_host_config(**host_settings)
    return {
        "image"      : fiddle.docker_image,
        "ports"      : [int(fiddle.internal_port)],
        "volumes"    : [INTERNAL_ROOT],
        "working_dir": INTERNAL_ROOT,
        "command"    : fiddle.startup_command,
        "name"       : fiddle.hash,
        "host_config": host_config,
        "detach"     : True
    }


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


def read_files_from_disc( directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            path = os.path.join(BASE_DIR, root, name)
            if path.startswith(directory, ):
                path = path.replace(directory, '', 1)
            with open(os.path.join(root, name)) as source:
                yield path, source.read()


def copy_fiddle(fiddle):
    fiddle.id, fiddle.pk = None, None
    fiddle.save()
    for file in fiddle.fiddlefile_set.all():
        file.id, file.pk = None, None
        file.fiddle = fiddle
        file.save()
    return fiddle