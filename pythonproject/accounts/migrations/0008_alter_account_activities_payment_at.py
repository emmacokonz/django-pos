# Generated by Django 4.1 on 2022-12-13 20:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_account_activities_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_activities',
            name='payment_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
