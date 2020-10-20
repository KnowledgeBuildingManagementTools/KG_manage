# Generated by Django 2.1.11 on 2020-10-17 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Noumenon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noumenon_name', models.TextField(null=True, verbose_name='本体名称')),
                ('noumenon_attribute', models.TextField(null=True, verbose_name='本体属性')),
            ],
            options={
                'verbose_name': 'benti表',
                'verbose_name_plural': 'benti表',
                'db_table': 'noumenon',
            },
        ),
    ]