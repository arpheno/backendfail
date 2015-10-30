import os
from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.db import models
from fabric.context_managers import lcd
from fabric.operations import local
from model_utils.managers import InheritanceManager

# Create your models here.
from fiddles.tasks import launch_container
from settings.basic import BASE_DIR


def get_upload_path(instance, filename):
    return os.path.join(instance.fiddle.name, filename)


def create_file(path, content):
    import os
    print path
    try:
        dirpath = os.path.join(BASE_DIR, os.path.join(os.path.split(path)[0]))
        os.makedirs(dirpath)
    except OSError as e:
        pass
    with open(os.path.join(BASE_DIR, path), 'w') as file:
        file.write(content)


class Fiddle(models.Model):
    hash = models.CharField(max_length=32, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(AUTH_USER_MODEL)
    objects = InheritanceManager()

    @property
    def internal_port(self):
        """ This property specifies the port the webserver is listening on inside the container.
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError("This should be implemented by every subclass of Fiddle")

    @property
    def startup_command(self):
        """ This property specifies a command that should be executed by the container on
        the commandline when it starts up.
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError("This should be implemented by every subclass of Fiddle")

    @property
    def docker_image(self):
        """ This property specifies an image from the docker hub that should be run.
        It should expect the user sources under /usr/src/app/
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError("This should be implemented by every subclass of Fiddle")

    @property
    def entrypoint(self):
        """ This property defines the path to the file that a user should
        be redirected to when they create a new fiddle.
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError("This should be implemented by every subclass of Fiddle")

    @property
    def prefix(self):
        """ This property defines where the project skeleton
        is located. `Fiddle` will walk that directory and create `FiddleFiles`
        based on the skeleton, when a new `Fiddle` instance is created.
        For an example see `DjangoFiddle`.  """
        raise NotImplementedError("This should be implemented by every subclass of Fiddle")

    def _launch(self):
        """ Launches the docker container asynchronously via celery"""
        self.port = launch_container(self.hash, self.docker_image, self.internal_port, self.startup_command)
        self.save()

    def spawn(self):
        self._hash()
        self._write_files()
        self._launch()

    def _hash(self):
        import hashlib
        self.hash = hashlib.md5(''.join(fiddlefile.content for fiddlefile in self.fiddlefile_set.all())).hexdigest()
        self.save()
        return self.hash

    def cleanup(self):
        self._stop()
        # self._delete_files()

    def _stop(self):
        with lcd(os.path.join(BASE_DIR, 'containers')):
            local('docker stop -t 1 ' + self.hash)

    def _remove(self):
        with lcd(os.path.join(BASE_DIR, 'containers')):
            local('docker rm ' + self.hash)

    def _delete_files(self):
        with lcd(os.path.join(BASE_DIR, 'containers')):
            local("rm -rf " + self.hash)

    def _write_files(self):
        root = os.path.join(BASE_DIR, "containers", self.hash)
        for fiddlefile in self.fiddlefile_set.all():
            create_file(os.path.join(root, fiddlefile.path), fiddlefile.content)

    def get_absolute_url(self):
        return reverse_lazy('fiddle-detail', kwargs={"pk": self.id})

    def create_file(self, path, content):
        obj = FiddleFile.objects.create(
            content=content, path=path,
            fiddle=self)
        obj.save()

    def save(self, *args, **kwargs):
        if not self.id:
            result = super(Fiddle, self).save(*args, **kwargs)
            for root, dirs, files in os.walk(self.prefix, topdown=False):
                for name in files:
                    path = os.path.join(BASE_DIR, root, name)
                    if path.startswith(self.prefix, ):
                        path = path.replace(self.prefix, '', 1)
                    print path
                    with open(os.path.join(root, name)) as source:
                        self.create_file(path, source.read())
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
