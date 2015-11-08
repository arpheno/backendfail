from celery import shared_task
from docker import Client
from fiddles.helpers import build_container_config, get_container_by_name, public_port, \
    DoesNotExist

DOCKER_SOCKET = 'unix://var/run/docker.sock'


@shared_task
def start_container(fiddle):
    """ This task takes care of launching docker containers. """
    # Let's get a hold of the docker socket first.
    api = Client(base_url=DOCKER_SOCKET)
    # Now we do some ugly mangling to get a configuration dict
    container_config = build_container_config(fiddle)

    try:  # Let's try to start the container first, maybe it has already been created.
        container = get_container_by_name(api, fiddle.hash)
    except DoesNotExist:  # ...nope, let's create the container.
        container = api.create_container(**container_config)

    api.start(container["Id"])
    return public_port(get_container_by_name(api, fiddle.hash))


@shared_task
def stop_container(hash):
    """ This task takes care of stopping docker containers. """
    api = Client(base_url=DOCKER_SOCKET)
    container = get_container_by_name(api, hash)
    api.stop(container["Id"])


@shared_task
def remove_container(fiddle):
    """ This task takes care of stopping docker containers. """
    api = Client(base_url=DOCKER_SOCKET)
    container = get_container_by_name(api, fiddle.hash)
    api.remove_container(container["Id"])
