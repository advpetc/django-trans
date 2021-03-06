# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-23 02:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_content', models.TextField(null=True)),
                ('trans_time', models.DateTimeField(blank=True, null=True)),
                ('vote_result', models.IntegerField(default=0)),
                ('vote_time', models.DateTimeField(blank=True, null=True)),
                ('bogus_score', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_engine', models.CharField(max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_source', models.TextField(null=True)),
                ('trans_source_lang', models.CharField(max_length=2, null=True)),
                ('trans_output_lang', models.CharField(max_length=2, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.CharField(max_length=100, null=True)),
                ('user_trans', models.TextField(null=True)),
                ('trans_his', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='project.TransHistory')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='result_details_view',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='transresult',
            name='trans_source',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='project.TransSource'),
        ),
        migrations.AddField(
            model_name='transhistory',
            name='trans_result',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='project.TransResult'),
        ),
        migrations.AddField(
            model_name='comment',
            name='trans_his',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='project.TransHistory'),
        ),
    ]
