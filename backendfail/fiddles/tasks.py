import os
import re
from random import randint
from celery import shared_task
from fabric.context_managers import lcd
from fabric.operations import local
from settings.basic import BASE_DIR


@shared_task
def launch_container(hash, image, internal_port, startup_command):
    internal_port = str(internal_port)
    image = str(image)
    command = str(startup_command)
    with lcd(os.path.join(BASE_DIR, 'containers', hash)):
        while True:  # Try to find a free port
            exposed_port = randint(8050, 12000)
            try:
                cmd = ["docker run"]
                cmd.append('--name ' + hash)
                cmd.append('-v "$PWD":/usr/src/app')
                cmd.append('-w /usr/src/app')
                cmd.append('-p ' + str(exposed_port) + ':' + internal_port + '')
                cmd.append('-d')
                cmd.append(image)
                cmd.append('bash -c "' + command + '"')
                cmd.append('> /dev/null 2>&1')
                local(' '.join(cmd))
                return exposed_port
            except SystemExit as e:
                print e
                ps = local("docker start " + hash + ' > /dev/null 2>&1 && docker ps --all | grep ' + hash,
                           capture=True)
                exposed_port = re.search(r".*?:(\d{4,5})", ps).group(1)
                return exposed_port
