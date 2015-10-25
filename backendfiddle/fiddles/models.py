import os
from random import randint

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse_lazy
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

def create_file(path,content):
    import os
    print path
    try:
        os.makedirs(os.path.join(os.path.split(path)[0]))
    except OSError:
        pass
    with open(path,'w') as file:
        file.write(content)
class Fiddle(models.Model):
    name = models.CharField(max_length=20, unique=True)
    hash = models.CharField(max_length=32,null=True,blank=True)
    port = models.IntegerField(null=True,blank=True)
    objects = InheritanceManager()
    def spawn(self):
        self._hash()
        self._write_files()
        self._launch()
    def cleanup(self):
        self._stop()
        # self._delete_files()
    def _stop(self):
        with lcd(os.path.join('containers')):
            local('docker stop '+self.hash+' && docker rm '+self.hash)
    def _delete_files(self):
        with lcd(os.path.join('containers')):
            local("rm -rf " + self.hash)
    def _launch(self):
        with lcd(os.path.join('containers',self.hash)):
            while True: # Try to find a free port
                port = randint(8001,12000)
                try:
                    cmd = ["docker run"]
                    cmd.append('--name '+self.hash)
                    cmd.append('-v "$PWD":/usr/src/app')
                    cmd.append('-w /usr/src/app')
                    cmd.append('-p '+str(port)+':8000')
                    cmd.append('-d django')
                    cmd.append('bash -c "python manage.py runserver 0.0.0.0:8000"')
                    local(' '.join(cmd))
                    self.port = port
                    self.save()
                    break
                except:
                    pass

    def _hash(self):
        import hashlib
        self.hash = hashlib.md5(''.join(fiddlefile.content for fiddlefile in self.fiddlefile_set.all())).hexdigest()
        self.save()
        return self.hash
    def _write_files(self):
        root = os.path.join("containers",self.hash)
        for fiddlefile in self.fiddlefile_set.all():
            create_file(os.path.join(root, fiddlefile.path),fiddlefile.content)
    def get_absolute_url(self):
        return reverse_lazy('fiddle-detail',kwargs={"pk":self.id})
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
    def get_absolute_url(self):
        return self.fiddle.get_absolute_url()+'/'+self.path


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
