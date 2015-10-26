import os
from random import randint

from fabric.context_managers import lcd
from fabric.operations import local

# Create your models here.
from fiddles.models import Fiddle
from constants import MANAGE_CONTENT, SETTINGS_CONTENT, VIEWS_CONTENT, MODELS_CONTENT, WSGI_CONTENT
from constants import URLS_CONTENT


class DjangoFiddle(Fiddle):
    def save(self, *args, **kwargs):
        if not self.id:
            result = super(DjangoFiddle, self).save(*args, **kwargs)
            self.create_file("manage.py", MANAGE_CONTENT)
            self.create_file("urls.py", URLS_CONTENT)
            self.create_file("wsgi.py", WSGI_CONTENT)
            self.create_file("settings.py", SETTINGS_CONTENT)
            self.create_file("__init__.py", "")
            self.create_file("app/models.py", MODELS_CONTENT)
            self.create_file("app/views.py", VIEWS_CONTENT)
            self.create_file("app/__init__.py", "")
            self.create_file("app/templates/app/app.html", "")
        else:
            result = super(DjangoFiddle, self).save(*args, **kwargs)
        return result

    def _launch(self):
        with lcd(os.path.join('containers', self.hash)):
            while True:  # Try to find a free port
                port = randint(8001, 12000)
                try:
                    cmd = ["docker run"]
                    cmd.append('--name ' + self.hash)
                    cmd.append('-v "$PWD":/usr/src/app')
                    cmd.append('-w /usr/src/app')
                    cmd.append('-p ' + str(port) + ':8000')
                    cmd.append('-d django')
                    cmd.append('bash -c "python manage.py runserver 0.0.0.0:8000"')
                    local(' '.join(cmd))
                    self.port = port
                    self.save()
                    break
                except:
                    pass
