# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import fiddles.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fiddle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='FiddleFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=fiddles.models.get_upload_path)),
                ('fiddle', models.ForeignKey(to='fiddles.Fiddle')),
            ],
        ),
    ]
