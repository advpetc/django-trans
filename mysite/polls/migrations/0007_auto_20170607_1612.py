# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-07 08:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_auto_20170607_1608'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Trans_output',
            new_name='SingleResult',
        ),
    ]
