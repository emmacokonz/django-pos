from itertools import product
from operator import mod
from tkinter import CASCADE
import datetime
from django.utils import timezone
from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User

#from pythonproject.productmgt.views import invoice

# Create your models here.
class Products(models.Model):
    STATUS_CHOICE = (
        ('in-stock', "IN STOCK"),
        ('out-of-stock', "OUT OF STOCK"),
        ('disabled', "Disabled")
    )
    name = models.CharField(blank=False, max_length=150, unique=True)
    description = models.CharField(max_length=500)
    brand = models.CharField(max_length=120, blank=True, null=True)
    opening_stock = models.DecimalField(decimal_places=1, default=0.0, max_digits=9,null=True, blank=True, verbose_name="Opening tock")
    quantity = models.DecimalField(decimal_places=1, default=0.0, max_digits=9)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cost_price = models.DecimalField(decimal_places=2, default=0.00, max_digits=20)
    selling_price = models.DecimalField(decimal_places=2, default=0.00, max_digits=20)
    status = models.CharField(max_length=20, default='out-of-stock', choices=STATUS_CHOICE)
    modified_at = models.DateTimeField(default=timezone.now)
    product_code = models.CharField(blank=False,  max_length=15, unique=True)
    reorder_point = models.PositiveIntegerField(default=0)
    attributes = models.CharField(max_length=1000, blank=True)
    
    def __str__(self):
        return self.name
    
class user_products(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.User.name, self.Products.name
    
class People(models.Model):
    TYPE_CHOICE=(
        ("customer","Customer"),
        ("vendor", "Vendor")
    )
    STATUS_CHOICE=(
        ("disabled","Disabled"),
        ("active", "Active")
    )
    name = models.CharField(max_length= 120, blank=False)
    balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    status = models.CharField(choices=STATUS_CHOICE,max_length=50,default='active')
    people_type = models.CharField(max_length=50, choices=TYPE_CHOICE, default='customer')
    address = models.CharField( max_length=250, null=True)
    
    def __str__(self):
        return self.name


class Invoice(models.Model):
    CHOICE_OPTION = (
        ('sales', "Sales"),
        ('purchase', 'Purchase'),
        ('sales_return', "Sales Return"),
        ('purchase_return', "Purchase Return"),
    )
    invoice_no = models.CharField(max_length=80, blank=True)
    total_quantity = models.DecimalField(decimal_places=1, default=0.0, max_digits=9)
    invoice_amount = models.DecimalField(decimal_places=2, default=0.00, max_digits=20)
    invoice_at = models.DateTimeField(default=timezone.now)
    people = models.ForeignKey(People, on_delete=models.SET_NULL, null=True)
    invoice_type = models.CharField(max_length=20,choices=CHOICE_OPTION)
    
    def __str__(self):
        return self.invoice_no
    
    def save(self, *args, **kwargs):
        today = datetime.date.today()
        if self.invoice_type == 'sales':
            today_string = "INV-"+today.strftime('%d%m%y')
        elif self.invoice_type == 'purchase':
            today_string = "PUR-"+today.strftime('%d%m%y')
        next_invoice_number = '0001'
        last_invoice = Invoice.objects.filter(invoice_no__startswith =today_string).order_by('invoice_no').last()
        if last_invoice :
            last_invoice_number = int(last_invoice.invoice_no[10:])
            next_invoice_number = '{0:04d}'.format(last_invoice_number + 1)
        self.invoice_no = today_string + next_invoice_number
        super(Invoice, self).save(*args, **kwargs)
    
class InvoiceActivities(models.Model):
    invoice_no = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True)
    products = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True)
    quantity = models.DecimalField(decimal_places=1, default='', max_digits=9)
    price = models.DecimalField(decimal_places=2, default='', max_digits=20)
    invoiced_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.id
    
class Accounts(models.Model):
    STATUS_CHOICE=(
        ('bank', 'Bank Accounts'),
        ('static', 'Static Accounts')
    )
    name = models.CharField(max_length=120, blank=False)
    description = models.CharField(max_length=120)
    type = models.CharField(max_length=50, choices=STATUS_CHOICE)

    def __str__(self):
        return self.name

class Payments(models.Model):
    people = models.ForeignKey(People, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(default=0.00, decimal_places=2,max_digits=20)
    payment_at = models.DateTimeField(default=timezone.now)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey(Accounts, on_delete=models.SET_NULL, null=True)
    payment_type = models.CharField(max_length=50)
    
    def __str__(self):
        return self.people
 