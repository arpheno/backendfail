import os
import re
from random import randint
from celery import shared_task
from fabric.context_managers import lcd
from fabric.operations import local
from settings.basic import BASE_DIR


@shared_task
def launch_container(hash, image, internal_port, startup_command):
    """
    :param hash: The hash of the Fiddle to start. It will become the name of the container
    :param image: The image that we should launch
    :param internal_port: The port that the internal webserver of the framework listens on
    :param startup_command: The command that should be executed on startup
    :return: The exposed port
    """
    internal_port = str(internal_port)
    image = str(image)
    command = str(startup_command)
    while True:  # Try to find a fre port
        exposed_port = randint(8050, 12000)
        try:
            ps = local("docker start " + hash + '  && docker ps --all | grep ' + hash,
                       capture=True)
            exposed_port = re.search(r".*?:(\d{4,5})", ps).group(1)
            return exposed_port
        except SystemExit as e:
            # We should replace this with docker-py
            cmd = ["docker run"]
            cmd.append('--name ' + hash)
            cmd.append('-v /var/containers/' + hash + ':/usr/src/app')
            cmd.append('-w /usr/src/app')
            cmd.append('-p ' + str(exposed_port) + ':' + internal_port + '')
            cmd.append('-d')
            cmd.append(image)
            cmd.append(command)
            local(' '.join(cmd))
            return exposed_port
