# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Fiddle',
            fields=[
                ('id', models.CharField(max_length=42, serialize=False, primary_key=True)),
                ('hash', models.CharField(max_length=32, null=True, blank=True)),
                ('port', models.IntegerField(null=True, blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FiddleFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('path', models.CharField(max_length=50)),
                ('fiddle', models.ForeignKey(to='fiddles.Fiddle')),
            ],
        ),
    ]
