# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0002_auto_20150707_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetprice',
            name='date',
            field=models.DateField(verbose_name='date'),
        ),
    ]
