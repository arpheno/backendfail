import json
import os
from random import randint
from fabric.context_managers import lcd
from fabric.operations import local
# Create your models here.
from fiddles.models import Fiddle
from settings.basic import BASE_DIR
import os


class DjangoFiddle(Fiddle):
    def save(self, *args, **kwargs):
        prefix = os.path.join(BASE_DIR, "dj", "skeleton/")
        if not self.id:
            result = super(DjangoFiddle, self).save(*args, **kwargs)
            for root, dirs, files in os.walk(prefix, topdown=False):
                for name in files:
                    path = os.path.join(BASE_DIR, root, name)
                    if path.startswith(prefix, ):
                        path = path.replace(prefix, '', 1)
                    print path
                    with open(os.path.join(root, name)) as source:
                        self.create_file(path, source.read())
        else:
            result = super(DjangoFiddle, self).save(*args, **kwargs)
        return result

    def _launch(self):
        command = "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
        with lcd(os.path.join(BASE_DIR, 'containers', self.hash)):
            while True:  # Try to find a free port
                port = randint(8001, 12000)
                try:
                    cmd = ["docker run"]
                    cmd.append('--name ' + self.hash)
                    cmd.append('-v "$PWD":/usr/src/app')
                    cmd.append('-w /usr/src/app')
                    cmd.append('-p ' + str(port) + ':8000')
                    cmd.append('-d django')
                    cmd.append('bash -c "' + command + '"')
                    local(' '.join(cmd), capture=True)
                    self.port = port
                    self.save()
                    break
                except SystemExit as e:
                    if self.hash in local("docker ps --all", capture=True):
                        local("docker start " + self.hash)
                        container = json.loads(local("docker inspect " + self.hash, capture=True))[0]
                        port = container["NetworkSettings"]["Ports"]["8000/tcp"][0]["HostPort"]
                        self.port = port
                        self.save()
                        break
