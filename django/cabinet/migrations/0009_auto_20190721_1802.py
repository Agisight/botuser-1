# Generated by Django 2.2.2 on 2019-07-21 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0008_auto_20190702_1807'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compaign',
            name='file',
        ),
        migrations.AddField(
            model_name='botuser',
            name='otpiska',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='compaign',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='compaign/'),
        ),
        migrations.AddField(
            model_name='compaign',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='compaign/'),
        ),
    ]