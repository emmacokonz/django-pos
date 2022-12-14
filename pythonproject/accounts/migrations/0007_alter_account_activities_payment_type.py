# Generated by Django 4.1 on 2022-11-27 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_account_activities_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_activities',
            name='payment_type',
            field=models.CharField(blank=True, choices=[('', 'Select payment type'), ('bill', 'Payment to Vendor or Supplier'), ('sales', 'Payment from customer')], default='', max_length=50, null=True),
        ),
    ]
