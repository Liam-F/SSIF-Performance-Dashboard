# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0011_auto_20150723_2206'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquityManager',
            fields=[
                ('managerid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('desc', models.CharField(max_length=500)),
                ('linkedin', models.CharField(max_length=100)),
                ('twitter', models.CharField(max_length=100)),
                ('profile', models.ImageField(width_field=215, height_field=322, upload_to='managers/')),
            ],
        ),
        migrations.RemoveField(
            model_name='sectormanager',
            name='assetid',
        ),
        migrations.DeleteModel(
            name='SectorManager',
        ),
    ]
