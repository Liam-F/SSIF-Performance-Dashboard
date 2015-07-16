# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_auto_20150714_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetdividend',
            name='dps',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='assetprice',
            name='price',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='cash',
            field=models.FloatField(unique_for_date='date'),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='value',
            field=models.FloatField(unique_for_date='date'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='shares',
            field=models.FloatField(),
        ),
    ]
