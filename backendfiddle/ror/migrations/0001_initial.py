# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fiddles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RailsFiddle',
            fields=[
                ('fiddle_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fiddles.Fiddle')),
            ],
            bases=('fiddles.fiddle',),
        ),
    ]
