# Generated by Django 4.1 on 2022-11-15 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounts',
            name='account_balance',
            field=models.DecimalField(blank=True, decimal_places=2, default='', max_digits=9, null=True, verbose_name='Current Balance'),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='opening_balance',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, null=True, verbose_name='Opening Balance'),
        ),
    ]