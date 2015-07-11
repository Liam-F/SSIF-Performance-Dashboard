# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0004_auto_20150707_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetprice',
            name='date',
            field=models.DateTimeField(unique_for_date='date'),
        ),
    ]
