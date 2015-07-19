# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_auto_20150716_0012'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectorManager',
            fields=[
                ('managerid', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('assetid', models.ForeignKey(to='data.Asset')),
            ],
        ),
    ]
