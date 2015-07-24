# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0010_sectormanager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectormanager',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
