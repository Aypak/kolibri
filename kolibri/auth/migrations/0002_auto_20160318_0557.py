# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-18 05:57
from __future__ import unicode_literals

import django.db.models.deletion
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kolibriauth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', mptt.fields.TreeForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kolibriauth.Collection')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kolibriauth.FacilityDataset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kolibriauth.FacilityUser')),
            ],
        ),
        migrations.AlterField(
            model_name='role',
            name='kind',
            field=models.CharField(choices=[(b'admin', 'Admin'), (b'coach', 'Coach')], max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('user', 'collection')]),
        ),
    ]
