# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-31 16:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Viewing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='date')),
                ('threshold', models.IntegerField(choices=[(0, 'Any'), (60, '1 minute'), (120, '2 minutes'), (300, '5 minutes')], default=0)),
                ('user_qty', models.IntegerField(default=0)),
                ('ips_qty', models.IntegerField(default=0)),
                ('stream_type', models.CharField(choices=[('live', 'Live'), ('vod', 'VOD'), ('all', 'All')], default='all', max_length=10)),
                ('avg_played_seconds', models.IntegerField(default=0)),
                ('total_played_seconds', models.IntegerField(default=0)),
                ('max_played_seconds', models.IntegerField(default=0)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
