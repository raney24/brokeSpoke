# Generated by Django 3.0.4 on 2020-05-13 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_newsystemuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='paymentStatus',
            field=models.CharField(blank=True, choices=[('Complete', 'Complete'), ('Pending', 'Pending')], default=0, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='transactions',
            name='paymentType',
            field=models.CharField(blank=True, choices=[('Cash/Credit', 'Cash/Credit'), ('Sweat Equity', 'Sweat Equity')], default=0, max_length=20, null=True),
        ),
    ]