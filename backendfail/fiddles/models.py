import hashlib
import os
import datetime
from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.db import models
from model_utils.managers import InheritanceManager
# Create your models here.
from fiddles.tasks import start_container, stop_container, create_container
from fiddles.helpers import write_file_to_disk, read_files_from_disc


class Fiddle(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    hash = models.CharField(max_length=32, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(AUTH_USER_MODEL, null=True, blank=True)
    objects = InheritanceManager()

    @property
    def internal_port(self):
        """ The port the webframework is listening on inside the container."""
        raise NotImplementedError("Should be implemented by every subclass of Fiddle")

    @property
    def startup_command(self):
        """ The command that should be run in the container when it starts up."""
        raise NotImplementedError("Should be implemented by every subclass of Fiddle")

    @property
    def docker_image(self):
        """Image from the docker hub to run. The skeleton will mount at /usr/src/app/"""
        raise NotImplementedError("Should be implemented by every subclass of Fiddle")

    @property
    def entrypoint(self):
        """ The file that a user should be redirected to when they create a new fiddle."""
        raise NotImplementedError("Should be implemented by every subclass of Fiddle")

    @property
    def prefix(self):
        """ Where the project skeleton is located. """
        raise NotImplementedError("Should be implemented by every subclass of Fiddle")

    def spawn(self):
        # Launch the docker container
        self.write_to_disc()
        self.port = start_container(self.id, self.internal_port)
        self.save()

    def cleanup(self):
        stop_container.delay(self.id)

    def create_file(self, path, content):
        config = {
            "content": content,
            "path"   : path,
            "fiddle" : self
        }
        FiddleFile.objects.create(**config).save()

    def save(self, *args, **kwargs):
        """`Fiddle` will walk its prefix directory and create `FiddleFiles`
        based from it, when a new `Fiddle` instance is created."""
        if not self.id:  # A new fiddle! Let's create its files.
            self.id, self.hash = create_container(self.internal_port,
                                                  self.docker_image,
                                                  self.startup_command)
            result = super(Fiddle, self).save(*args, **kwargs)
            for path, content in read_files_from_disc(self.prefix):
                self.create_file(path, content)
        else:  # ... this fiddle already had its files created.
            result = super(Fiddle, self).save(*args, **kwargs)
        return result

    @property
    def root(self):
        return os.path.join("/var/containers", self.hash)

    def write_to_disc(self):
        for file in self.fiddlefile_set.all():
            path = os.path.join(self.root, file.path)
            write_file_to_disk(path, file.content)


class FiddleFile(models.Model):
    fiddle = models.ForeignKey('fiddles.Fiddle')
    content = models.TextField()
    path = models.CharField(max_length=50)

    def clean(self):
        if self.path[0] in "*/":
            raise ValidationError("No absolute paths allowed.")
        if ".." in self.path:
            raise ValidationError("'..' is not a valid path.")
        if "$" in self.path:
            raise ValidationError("Environment variables are not allowed.")
        return super(FiddleFile, self).clean()
