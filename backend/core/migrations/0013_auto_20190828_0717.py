# Generated by Django 2.1.5 on 2019-08-27 22:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_user_max_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='max_quantity',
            new_name='max_quantity_perc',
        ),
    ]
