import json
import os
import re
from random import randint
from fabric.context_managers import lcd
from fabric.operations import local
# Create your models here.
from dj.tasks import launch_django
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
        self.port = launch_django(self.hash).delay().get()
        self.save()
