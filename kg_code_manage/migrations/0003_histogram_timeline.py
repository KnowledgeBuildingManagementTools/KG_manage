# Generated by Django 2.0.1 on 2020-10-23 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kg_code_manage', '0002_auto_20201022_1533'),
    ]

    operations = [
        migrations.CreateModel(
            name='Histogram',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('class_name', models.CharField(max_length=50, verbose_name='种类名称')),
                ('time', models.DateTimeField(verbose_name='时间')),
                ('require_count', models.CharField(max_length=50, verbose_name='需求个数')),
            ],
        ),
        migrations.CreateModel(
            name='timeline',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('time', models.DateTimeField(verbose_name='时间')),
                ('event_name', models.CharField(max_length=100, verbose_name='事件名称')),
                ('event_content', models.CharField(max_length=2000, verbose_name='事件内容')),
            ],
        ),
    ]