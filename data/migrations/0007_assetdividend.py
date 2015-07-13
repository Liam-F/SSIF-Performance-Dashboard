# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_auto_20150711_2158'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetDividend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('dps', models.DecimalField(decimal_places=2, max_digits=5)),
                ('assetid', models.ForeignKey(to='data.Asset', unique_for_date='date')),
            ],
        ),
    ]
