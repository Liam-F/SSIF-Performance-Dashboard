# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('assetid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('ticker', models.CharField(max_length=5)),
                ('industry', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='AssetPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(unique_for_date='date')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('assetid', models.ForeignKey(to='data.Asset')),
            ],
        ),
    ]
