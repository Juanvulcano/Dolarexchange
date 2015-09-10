# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0006_auto_20150907_0459'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='ci',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='CI',
            field=models.IntegerField(default=0, blank=True),
            preserve_default=False,
        ),
    ]
