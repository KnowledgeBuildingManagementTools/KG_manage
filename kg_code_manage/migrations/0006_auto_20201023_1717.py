# Generated by Django 2.0.1 on 2020-10-23 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kg_code_manage', '0005_auto_20201023_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='histogram',
            name='require_count',
            field=models.CharField(max_length=50, verbose_name='个数'),
        ),
        migrations.AlterField(
            model_name='timeline',
            name='time',
            field=models.DateField(verbose_name='时间'),
        ),
    ]