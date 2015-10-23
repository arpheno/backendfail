import os

from django.core.files.base import ContentFile
from django.db import models
from model_utils.managers import InheritanceManager

from django.db import models

# Create your models here.
from settings.django import MANAGE_CONTENT, SETTINGS_CONTENT, VIEWS_CONTENT, MODELS_CONTENT
from settings.django import URLS_CONTENT


def get_upload_path(instance, filename):
    return os.path.join(instance.fiddle.name, filename)


class Fiddle(models.Model):
    name = models.CharField(max_length=20, unique=True)
    objects = InheritanceManager()
    def create_file(self,filename, content):
        obj = FiddleFile.objects.create(
            file=ContentFile(content, name=filename),
            fiddle=self)
        obj.save()



class FiddleFile(models.Model):
    fiddle = models.ForeignKey('fiddles.Fiddle')
    file = models.FileField(upload_to=get_upload_path)


class DjangoFiddle(Fiddle):
    def save(self, *args, **kwargs):
        if not self.id:
            result = super(DjangoFiddle, self).save(*args, **kwargs)

            self.create_file("manage.py",MANAGE_CONTENT)
            self.create_file("urls.py",URLS_CONTENT)
            self.create_file("settings.py",SETTINGS_CONTENT)
            self.create_file("__init__.py","")
            self.create_file("app/models.py",MODELS_CONTENT)
            self.create_file("app/views.py",VIEWS_CONTENT)
            self.create_file("app/__init__.py","")
        else:
            result = super(DjangoFiddle, self).save(*args, **kwargs)
        return result
