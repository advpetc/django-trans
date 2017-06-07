# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-07 08:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_transresult_trans_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trans_output',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='transresult',
            name='trans_output',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.Trans_output'),
        ),
    ]