# Generated by Django 3.0.4 on 2022-02-03 15:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_auto_20200906_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timelogs',
            name='endTime',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 3, 10, 57, 21, 359270)),
        ),
        migrations.AlterField(
            model_name='timelogs',
            name='startTime',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 3, 10, 57, 21, 359238)),
        ),
    ]
