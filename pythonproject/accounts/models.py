from itertools import product
from operator import mod
from tkinter import CASCADE
from django.utils import timezone
from django.db import models
from productmgt.models import People
from django.contrib.auth.models import User


# Create your models here.
class Accounts(models.Model):
    ACCOUNT_TYPE_CHOICE = (
        ('','Select account type'),
        ('bank', "Bank"),
        ('expenses', "Expenses"),
    )
    name = models.CharField(blank=False, max_length=150, unique=True)
    description = models.CharField(max_length=500, blank=True)
    opening_balance = models.DecimalField(decimal_places=2, default=0.00, max_digits=24,null=True, blank=True)
    account_type = models.CharField(max_length=20, default='', choices=ACCOUNT_TYPE_CHOICE)
    account_balance = models.DecimalField(decimal_places=2, default=0.00, max_digits=9,blank=True)
    opening_balance_at = models.DateTimeField(default=timezone.now, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    

class Account_activities(models.Model):
    PAYMENT_TYPE_CHOICE =(
        ('', 'Select payment type'),
        ('bill', 'Payment to Vendor or Supplier'),
        ('sales', 'Payment from customer'),
    )
    to_account = models.ForeignKey(Accounts, on_delete=models.SET_NULL,null=True,related_name='to_account', blank=True)
    from_account = models.ForeignKey(Accounts, on_delete=models.SET_NULL,null=True, related_name='from_account', blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=24, null=True, blank=False)
    payment_type = models.CharField(max_length=50, default='',blank=True, choices=PAYMENT_TYPE_CHOICE,null=True)
    #payment_at = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    applied_by = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    applied_to = models.ForeignKey(People, on_delete=models.SET_NULL,null=True)
    description = models.CharField( max_length=250, null=True, blank=True)
    
    def __str__(self):
        return str(self.to_account)