from celery import shared_task
from docker.utils import create_host_config
from docker import Client


def get_container_by_name(client, name):
    return [c for c in client.containers(all=True) if "/" + name in c["Names"]][0]


@shared_task
def launch_container(fiddle):
    """
    This task takes care of launching the docker container.
    """
    image = str(fiddle.docker_image)
    container_root, internal_root = '/var/containers/', '/usr/src/app'
    ports, volumes = [int(fiddle.internal_port)], [internal_root]
    api = Client(base_url='unix://var/run/docker.sock')
    try:
        myc = get_container_by_name(api, fiddle.hash)
        api.start(myc["Id"])
        myc = get_container_by_name(api, fiddle.hash)
        return myc["Ports"][0]["PublicPort"]
    except IndexError as e:
        # The IndexError indicated that this container has never been run yet,
        # so we should create it.
        host_config = create_host_config(
            # We bind the internal server port to a high port, let docker take care of it
            port_bindings={int(fiddle.internal_port): None},
            # Also mount the skeleton to the container
            binds=[container_root + fiddle.hash + ':' + internal_root])
        # Now start this whole shebang
        container = api.create_container(
            image=image,
            ports=ports,
            volumes=volumes,
            working_dir=internal_root,
            command=fiddle.startup_command,
            name=fiddle.hash,
            host_config=host_config,
            detach=True)
        api.start(container["Id"])
        # We have to get the port from the container now
        myc = get_container_by_name(api, fiddle.hash)
        return myc["Ports"][0]["PublicPort"]
