# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-28 09:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_project_dis_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='freq',
            field=models.IntegerField(default=0),
        ),
    ]
