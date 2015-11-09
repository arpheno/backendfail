# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fiddles', '0002_auto_20151108_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fiddle',
            name='owner',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
