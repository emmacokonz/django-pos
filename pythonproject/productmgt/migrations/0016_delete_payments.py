# Generated by Django 4.1 on 2022-12-13 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productmgt', '0015_invoiceactivities_invoiced_at'),
    ]

    operations = [
        migrations.DeleteModel(
            name='payments',
        ),
    ]
