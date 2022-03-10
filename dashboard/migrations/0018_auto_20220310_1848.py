# Generated by Django 3.0.4 on 2022-03-10 18:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_auto_20220310_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timelogs',
            name='startTime',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 10, 18, 48, 45, 903564, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='users',
            name='lastVisit',
            field=models.CharField(blank=True, default='NULL', max_length=60),
        ),
    ]
