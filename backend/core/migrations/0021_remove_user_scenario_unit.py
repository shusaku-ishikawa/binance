# Generated by Django 2.1.5 on 2019-09-28 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20190928_1515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='scenario_unit',
        ),
    ]