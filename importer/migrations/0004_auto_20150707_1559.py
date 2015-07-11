# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0003_auto_20150707_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetprice',
            name='date',
            field=models.DateTimeField(verbose_name='date'),
        ),
    ]
