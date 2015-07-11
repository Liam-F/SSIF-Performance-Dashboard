# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20150710_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='cash',
            field=models.DecimalField(default=100000, decimal_places=3, max_digits=10),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='value',
            field=models.DecimalField(default=0, decimal_places=3, max_digits=10),
        ),
    ]
