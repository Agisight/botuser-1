# Generated by Django 2.2.2 on 2019-07-02 12:27

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0004_auto_20190628_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[]),
        ),
    ]
