# Generated by Django 4.1 on 2022-09-21 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productmgt', '0003_rename_amount_invoice_invoice_amount_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoiceactivities',
            old_name='product',
            new_name='products',
        ),
    ]
