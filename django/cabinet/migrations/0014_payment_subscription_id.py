# Generated by Django 2.2.2 on 2019-07-24 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0013_payment_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='subscription_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]