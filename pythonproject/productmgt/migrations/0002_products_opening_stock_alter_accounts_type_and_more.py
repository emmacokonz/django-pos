# Generated by Django 4.1 on 2022-09-19 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productmgt', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='opening_stock',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='type',
            field=models.CharField(choices=[('bank', 'Bank Accounts'), ('static', 'Static Accounts')], max_length=50),
        ),
        migrations.AlterField(
            model_name='people',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='products',
            name='attributes',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='products',
            name='status',
            field=models.CharField(choices=[(1, 'IN STOCK'), (0, 'OUT OF STOCK')], default=0, max_length=1),
        ),
    ]
