# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-19 02:46
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bid', '0006_auto_20171115_2222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bidsession',
            name='end_bid',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 19, 3, 46, 12, 870334, tzinfo=utc), verbose_name='End bid time'),
        ),
    ]