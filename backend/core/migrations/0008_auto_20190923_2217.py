# Generated by Django 2.1.5 on 2019-09-23 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20190923_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.IntegerField(null=True, verbose_name='orderId'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(max_length=100, null=True, verbose_name='ステータス'),
        ),
    ]
