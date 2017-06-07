# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-07 08:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0009_auto_20170607_1623'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_source', models.TextField(null=True)),
                ('trans_source_lang', models.CharField(max_length=2, null=True)),
                ('trans_source_type', models.CharField(max_length=2, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='transresult',
            name='trans_source_lang',
        ),
        migrations.AlterField(
            model_name='transresult',
            name='trans_source',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.TransSource'),
        ),
    ]