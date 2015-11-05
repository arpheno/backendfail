from celery import shared_task
from docker.utils import create_host_config
from docker import Client

api_base = 'unix://var/run/docker.sock'


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


@shared_task
def launch_container(fiddle):
    """
    This task takes care of launching the docker container.
    """
    api = Client(base_url=api_base)
    container_config = build_container_config(fiddle)
    try:
        started_container = get_container_by_name(api, fiddle.hash)
        api.start(started_container["Id"])
        return public_port(get_container_by_name(api, fiddle.hash))
    except DoesNotExist as e:
        container = api.create_container(**container_config)
        api.start(container["Id"])
        return public_port(get_container_by_name(api, fiddle.hash))
