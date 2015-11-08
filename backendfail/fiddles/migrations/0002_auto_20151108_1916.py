# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fiddles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fiddle',
            name='id',
            field=models.CharField(max_length=64, serialize=False, primary_key=True),
        ),
    ]
