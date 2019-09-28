# Generated by Django 2.1.5 on 2019-09-28 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_remove_user_transaction_fee_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='commission_rate',
            field=models.FloatField(default=0.075, verbose_name='手数料'),
        ),
    ]
