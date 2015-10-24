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
                ('hash', models.CharField(unique=True, max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='FiddleFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=fiddles.models.get_upload_path)),
                ('content', models.TextField()),
                ('path', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='DjangoFiddle',
            fields=[
                ('fiddle_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fiddles.Fiddle')),
            ],
            bases=('fiddles.fiddle',),
        ),
        migrations.AddField(
            model_name='fiddlefile',
            name='fiddle',
            field=models.ForeignKey(to='fiddles.Fiddle'),
        ),
    ]
