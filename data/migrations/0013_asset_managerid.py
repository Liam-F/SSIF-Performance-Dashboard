# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0012_auto_20150723_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='managerid',
            field=models.ForeignKey(default=1, to='data.EquityManager'),
            preserve_default=False,
        ),
    ]
