import hashlib
import os

from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.db import models
from fabric.operations import local
from model_utils.managers import InheritanceManager
# Create your models here.
from fiddles.tasks import start_container, stop_container, remove_container
from fiddles.helpers import write_file_to_disk
from settings.basic import BASE_DIR


def get_upload_path(instance, filename):
    pass


class Fiddle(models.Model):
    hash = models.CharField(max_length=32, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(AUTH_USER_MODEL)
    objects = InheritanceManager()

    @property
    def internal_port(self):
        """ This property specifies the port the webserver is listening on inside the
        container.
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError(
            "This should be implemented by every subclass of Fiddle")

    @property
    def startup_command(self):
        """ This property specifies a command that should be executed by the container on
        the commandline when it starts up.
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError(
            "This should be implemented by every subclass of Fiddle")

    @property
    def docker_image(self):
        """ This property specifies an image from the docker hub that should be run.
        It should expect the user sources under /usr/src/app/
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError(
            "This should be implemented by every subclass of Fiddle")

    @property
    def entrypoint(self):
        """ This property defines the path to the file that a user should
        be redirected to when they create a new fiddle.
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError(
            "This should be implemented by every subclass of Fiddle")

    @property
    def prefix(self):
        """ This property defines where the project skeleton
        is located. `Fiddle` will walk that directory and create `FiddleFiles`
        based on the skeleton, when a new `Fiddle` instance is created.
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError(
            "This should be implemented by every subclass of Fiddle")

    def spawn(self):
        self.hash = hashlib.md5(''.join(
            fiddlefile.content for fiddlefile in self.fiddlefile_set.all())).hexdigest()
        self.save()
        # Write the content of the files to disk.
        for fiddlefile in self.fiddlefile_set.all():
            write_file_to_disk(os.path.join(self.root, fiddlefile.path),
                               fiddlefile.content)
        # Launch the docker container
        self.port = start_container(self)
        self.save()

    def cleanup(self):
        stop_container(self).delay()

    def _remove(self):
        remove_container(self).delay()

    @property
    def root(self):
        return os.path.join("/var/containers", self.hash)

    def get_absolute_url(self):
        return reverse_lazy('fiddle-detail', kwargs={"pk": self.id})

    def create_file(self, path, content):
        config = {
            "content": content,
            "path"   : path,
            "fiddle" : self
        }
        FiddleFile.objects.create(**config).save()
    def read_files_from_disc(self, directory):
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                path = os.path.join(BASE_DIR, root, name)
                if path.startswith(directory, ):
                    path = path.replace(directory, '', 1)
                with open(os.path.join(root, name)) as source:
                    self.create_file(path, source.read())

    def save(self, *args, **kwargs):
        if not self.id:
            result = super(Fiddle, self).save(*args, **kwargs)
            self.read_files_from_disc(self.prefix)
        else:
            result = super(Fiddle, self).save(*args, **kwargs)
        return result


class FiddleFile(models.Model):
    fiddle = models.ForeignKey('fiddles.Fiddle')
    content = models.TextField()
    path = models.CharField(max_length=50)

    def clean(self):
        if self.path[0] in "*/$":
            raise ValidationError
        if ".." in self.path:
            raise ValidationError
        return super(FiddleFile, self).clean()

    def get_absolute_url(self):
        return self.fiddle.get_absolute_url() + '/' + self.path
