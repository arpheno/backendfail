import os

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from fabric.context_managers import lcd
from fabric.operations import local
from model_utils.managers import InheritanceManager
from django.db import models
# Create your models here.
from settings.django import MANAGE_CONTENT, SETTINGS_CONTENT, VIEWS_CONTENT, MODELS_CONTENT, WSGI_CONTENT
from settings.django import URLS_CONTENT


def get_upload_path(instance, filename):
    return os.path.join(instance.fiddle.name, filename)


class Fiddle(models.Model):
    name = models.CharField(max_length=20, unique=True)
    hash = models.CharField(max_length=32,unique=True)
    objects = InheritanceManager()
    def spawn(self):
        self._hash()
        self._write_files()
        self._launch()
    def _cleanup(self):
        self._stop()
        self._delete_files()
    def _stop(self):
        with lcd(os.path.join('containers')):
            local('docker stop '+self.hash+' && docker rm '+self.hash)
    def _delete_files(self):
        with lcd(os.path.join('containers')):
            local("rm -rf " + self.hash)
    def _launch(self):
        with lcd(os.path.join('containers',self.hash)):
            cmd = ["docker run"]
            cmd.append('--name '+self.hash)
            cmd.append('-v "$PWD":/usr/src/app')
            cmd.append('-w /usr/src/app')
            cmd.append('-p 8000:8000')
            cmd.append('-d django')
            cmd.append('bash -c "python manage.py runserver 0.0.0.0:8000"')
            local(' '.join(cmd))
    def _hash(self):
        import hashlib
        self.hash = hashlib.md5(''.join(fiddlefile.content for fiddlefile in self.fiddlefile_set.all())).hexdigest()
        self.save()
        return self.hash
    def _write_files(self):
        root = os.path.join("containers",self.hash)
        if not os.path.exists(root):
            os.makedirs(root)
            os.makedirs(os.path.join(root,'app'))
        for fiddlefile in self.fiddlefile_set.all():
            with open(os.path.join(root, fiddlefile.path),'w') as file:
                file.write(fiddlefile.content)

    def create_file(self, path, content):
        obj = FiddleFile.objects.create(
            content=content, path=path,
            fiddle=self)
        obj.save()


class FiddleFile(models.Model):
    fiddle = models.ForeignKey('fiddles.Fiddle')
    file = models.FileField(upload_to=get_upload_path)
    content = models.TextField()
    path = models.CharField(max_length=50)
    def clean(self):
        if self.path[0] in "*/$":
            raise ValidationError
        if ".."  in self.path:
            raise ValidationError
        return super(FiddleFile, self).clean()


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
        else:
            result = super(DjangoFiddle, self).save(*args, **kwargs)
        return result
