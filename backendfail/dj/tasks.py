import os
import re
from random import randint

from celery import shared_task
from fabric.context_managers import lcd
from fabric.operations import local

from settings.basic import BASE_DIR


@shared_task
def launch_django(hash):
    command = "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
    with lcd(os.path.join(BASE_DIR, 'containers', hash)):
        while True:  # Try to find a free port
            port = randint(8050, 12000)
            try:
                cmd = ["docker run"]
                cmd.append('--name ' + hash)
                cmd.append('-v "$PWD":/usr/src/app')
                cmd.append('-w /usr/src/app')
                cmd.append('-p ' + str(port) + ':8000')
                cmd.append('-d django')
                cmd.append('bash -c "' + command + '"')
                cmd.append('> /dev/null 2>&1')
                local(' '.join(cmd))
                return port
            except SystemExit as e:
                ps = local("docker start " + hash + '> /dev/null 2>&1 && docker ps --all | grep ' + hash,
                           capture=True)
                portregex = re.compile(r":\d{4,5}")

                port = re.search(r".*?:(\d{4,5})", ps).group(1)
                return port
