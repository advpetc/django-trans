# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-30 05:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_data_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='data',
            name='status',
        ),
        migrations.AddField(
            model_name='user',
            name='boundary',
            field=models.IntegerField(default=0),
        ),
    ]
