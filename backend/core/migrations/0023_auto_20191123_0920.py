# Generated by Django 2.1.5 on 2019-11-23 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20191029_0015'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='do_usd',
        ),
        migrations.AddField(
            model_name='user',
            name='do_usdt',
            field=models.BooleanField(default=True, verbose_name='USTD'),
        ),
    ]