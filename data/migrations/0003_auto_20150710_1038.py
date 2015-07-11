# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_holding_portfolio'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Holding',
            new_name='Transaction',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='holdingid',
            new_name='transid',
        ),
        migrations.RemoveField(
            model_name='portfolio',
            name='date',
        ),
        migrations.RemoveField(
            model_name='portfolio',
            name='holdings',
        ),
        migrations.AddField(
            model_name='portfolio',
            name='value',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='asset',
            name='name',
            field=models.CharField(unique=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='asset',
            name='ticker',
            field=models.CharField(unique=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='assetprice',
            name='assetid',
            field=models.ForeignKey(unique_for_date='date', to='data.Asset'),
        ),
        migrations.AlterField(
            model_name='assetprice',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
