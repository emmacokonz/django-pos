# Generated by Django 4.1 on 2022-09-27 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productmgt', '0010_alter_invoice_invoice_no_alter_products_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='people',
            name='people_type',
            field=models.CharField(choices=[('customer', 'Customer'), ('vendor', 'Vendor')], default='customer', max_length=50),
        ),
        migrations.AlterField(
            model_name='products',
            name='product_code',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='products',
            name='status',
            field=models.CharField(choices=[('in-stock', 'IN STOCK'), ('out-of-stock', 'OUT OF STOCK'), ('disabled', 'Disabled')], default='out-of-stock', max_length=20),
        ),
    ]
