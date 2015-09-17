# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_equitymanager_sector'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='noncash',
            field=models.BooleanField(default=False),
        ),
    ]
