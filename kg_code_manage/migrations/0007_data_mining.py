# Generated by Django 2.0.1 on 2020-10-24 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kg_code_manage', '0006_auto_20201023_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='Data_mining',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('label', models.CharField(max_length=100, verbose_name='节点标签')),
                ('uuid', models.CharField(max_length=100, verbose_name='节点唯一标识')),
                ('status', models.CharField(max_length=2000, verbose_name='状态')),
            ],
        ),
    ]
