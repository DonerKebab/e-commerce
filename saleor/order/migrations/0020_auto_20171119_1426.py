# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-19 07:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0019_auto_20171119_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordereditem',
            name='lazada_order_item_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='ordereditem',
            name='lazada_tracking_number',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]