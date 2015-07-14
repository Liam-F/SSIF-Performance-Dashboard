# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_assetdividend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolio',
            name='cash',
            field=models.DecimalField(max_digits=10, decimal_places=3, unique_for_date='date', default=1000000),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='value',
            field=models.DecimalField(max_digits=10, decimal_places=3, unique_for_date='date', default=0),
        ),
    ]
