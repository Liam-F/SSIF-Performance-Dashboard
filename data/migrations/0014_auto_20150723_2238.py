# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0013_asset_managerid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equitymanager',
            name='desc',
            field=models.CharField(max_length=2000),
        ),
    ]
