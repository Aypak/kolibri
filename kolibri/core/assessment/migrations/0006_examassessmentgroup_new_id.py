# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-04-01 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0005_auto_20240401_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='examassessmentgroup',
            name='new_id',
            field=models.UUIDField(null=True),
        ),
    ]
