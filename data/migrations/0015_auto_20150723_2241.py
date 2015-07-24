# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0014_auto_20150723_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equitymanager',
            name='profile',
            field=models.ImageField(upload_to='managers/'),
        ),
    ]
