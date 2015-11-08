from celery import shared_task
from docker import Client
from fiddles.helpers import build_container_config, get_container_by_name, public_port, \
    DoesNotExist

DOCKER_SOCKET = 'unix://var/run/docker.sock'


@shared_task
def create_container(internal_port,docker_image,startup_command):
    """ This task takes care of launching docker containers. """
    # Let's get a hold of the docker socket first.
    api = Client(base_url=DOCKER_SOCKET)
    container_config,hash = build_container_config(internal_port,
                                              docker_image,
                                              startup_command)
    container = api.create_container(**container_config)
    return container['Id'],hash


@shared_task
def start_container(id, internal_port):
    """ This task takes care of launching docker containers. """
    # Let's get a hold of the docker socket first.
    api = Client(base_url=DOCKER_SOCKET)
    api.start(id)
    return int(api.port(id, internal_port)[0]['HostPort'])


@shared_task
def stop_container(id):
    """ This task takes care of stopping docker containers. """
    api = Client(base_url=DOCKER_SOCKET)
    api.stop(id)


@shared_task
def remove_container(fiddle):
    """ This task takes care of stopping docker containers. """
    api = Client(base_url=DOCKER_SOCKET)
    container = get_container_by_name(api, fiddle.hash)
    api.remove_container(container["Id"])
