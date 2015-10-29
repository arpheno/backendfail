import json
import os
import re
from random import randint
from fabric.context_managers import lcd
from fabric.operations import local
# Create your models here.
from fiddles.models import Fiddle
from settings.basic import BASE_DIR
import os


class DjangoFiddle(Fiddle):
    @property
    def prefix(self):
        return os.path.join(BASE_DIR, "dj", "skeleton/")
    @property
    def entrypoint(self):
        return "app/templates/app/app.html"
    def save(self, *args, **kwargs):
        if not self.id:
            result = super(DjangoFiddle, self).save(*args, **kwargs)
            for root, dirs, files in os.walk(self.prefix, topdown=False):
                for name in files:
                    path = os.path.join(BASE_DIR, root, name)
                    if path.startswith(self.prefix, ):
                        path = path.replace(self.prefix, '', 1)
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
                port = randint(8050, 12000)
                try:
                    cmd = ["docker run"]
                    cmd.append('--name ' + self.hash)
                    cmd.append('-v "$PWD":/usr/src/app')
                    cmd.append('-w /usr/src/app')
                    cmd.append('-p ' + str(port) + ':8000')
                    cmd.append('-d django')
                    cmd.append('bash -c "' + command + '"')
                    cmd.append('> /dev/null 2>&1')
                    local(' '.join(cmd))
                    self.port = port
                    self.save()
                    break
                except SystemExit as e:
                    ps = local("docker start " + self.hash + '> /dev/null 2>&1 && docker ps --all | grep ' + self.hash,
                               capture=True)
                    portregex = re.compile(r":\d{4,5}")

                    port = re.search(r".*?:(\d{4,5})", ps).group(1)
                    self.port = port
                    self.save()
                    break
