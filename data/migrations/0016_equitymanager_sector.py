# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0015_auto_20150723_2241'),
    ]

    operations = [
        migrations.AddField(
            model_name='equitymanager',
            name='sector',
            field=models.CharField(default='na', max_length=50),
            preserve_default=False,
        ),
    ]
