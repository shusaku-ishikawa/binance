# Generated by Django 2.1.5 on 2019-09-28 03:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_user_scenario_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='transaction_fee_rate',
        ),
    ]