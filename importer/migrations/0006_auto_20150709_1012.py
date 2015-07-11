# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0005_auto_20150707_1614'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assetprice',
            name='assetid',
        ),
        migrations.DeleteModel(
            name='Asset',
        ),
        migrations.DeleteModel(
            name='AssetPrice',
        ),
    ]
