from django.db import models


# Create your models here.
class Blog(models.Model):
    """ Everyone needs a blog """
    name = models.CharField(max_length=100)


class Entry(models.Model):
    """ A blog entry """
    blog = models.ForeignKey(Blog)
    content = models.TextField()
