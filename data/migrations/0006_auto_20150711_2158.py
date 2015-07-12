# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_auto_20150710_2313'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 11, 21, 58, 3, 724450)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='cash',
            field=models.DecimalField(decimal_places=3, default=1000000, max_digits=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
