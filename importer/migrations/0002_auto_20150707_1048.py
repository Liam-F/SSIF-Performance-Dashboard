# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetprice',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
