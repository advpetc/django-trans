# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-16 19:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('polls', '0022_auto_20170615_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='transhistory',
            name='bogus_score',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='score',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
