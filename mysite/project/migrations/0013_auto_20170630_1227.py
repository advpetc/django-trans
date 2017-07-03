# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-30 12:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_auto_20170630_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='result',
            name='result',
            field=models.CharField(blank=True, max_length=4096, null=True),
        ),
        migrations.AlterField(
            model_name='result',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='project.User'),
        ),
    ]
