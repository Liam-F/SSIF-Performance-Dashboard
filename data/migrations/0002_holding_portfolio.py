# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holding',
            fields=[
                ('holdingid', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(unique_for_date='date')),
                ('shares', models.DecimalField(decimal_places=3, max_digits=10)),
                ('assetid', models.ForeignKey(to='data.Asset')),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('portfolioid', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(unique_for_date='date')),
                ('holdings', models.TextField()),
            ],
        ),
    ]
