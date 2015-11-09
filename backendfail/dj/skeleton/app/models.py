"""
Models

"""
"""
A model is the single, definitive source of
information about your data. It contains the
essential fields and behaviors of the data you're
storing. Generally, each model maps to a single
database table.

The basics:

* Each model is a Python class that subclasses django.db.models.Model.
* Each attribute of the model represents a database field.
"""

from django.db import models


# The blog model for the demo app
class Blog(models.Model):
    """ Everyone needs a blog """
    name = models.CharField(max_length=100)


# An example model
class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


"""
first_name and last_name are fields of the model.
Each field is specified as a class attribute,
and each attribute maps to a database column.

The above Person model would create a database table like this:

CREATE TABLE myapp_person (
    "id" serial NOT NULL PRIMARY KEY,
    "first_name" varchar(30) NOT NULL,
    "last_name" varchar(30) NOT NULL
);

For more information on models see
https://docs.djangoproject.com/en/1.8/topics/db/models/"""
