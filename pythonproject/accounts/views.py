
from datetime import datetime
from decimal import Decimal
from os import name
from turtle import st
from urllib.parse import urlparse
from django.contrib import messages
from django.http import Http404
from django.http import JsonResponse
from django.urls import reverse,resolve
from django.views.generic.base import View
from django.db.models import Sum,F,Q
from django.shortcuts import render,redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from .models import Accounts, Account_activities
from .forms import (Account_form, Payment_form)
from productmgt.models import People
from django.contrib.auth.models import User

BANK = 'bank'
EXPENSES = 'expenses'
CUSTOMER = 'customer'
VENDOR = 'vendor'
SALES = 'sales'
BILL = 'bill'
TRF = 'TRF'

# Create your views here.

class Dashboard(View):
    def get (self, request, *args, **kwargs):
        print("dashboard")
        return render(request, 'dashboard.html')
    
@login_required   
def index(request):
    accounts = Accounts.objects.all()
    
    context = {
        'accounts': accounts,
        'title': 'Accounts',
        'payable': calculate_payables()['payable_amount'],
        'receiveables': calculate_receiveables()['payable_amount'],
    }
    return render(request, 'accounts/index.html', context)

@login_required
def get_account(request, account_id):
    account_instance = Accounts.objects.get(pk = account_id)
    account_activities = Account_activities.objects.filter(Q(to_account = account_id) | Q(from_account = account_id)).order_by('-payment_at')
    
    for account_activity in account_activities:
        if account_activity.to_account == account_id:
            account_activities["account"] = account_activity.to_account
        elif account_activity.from_account == account_id:
            account_activities["account"] = account_activity.from_account
        
    
    
    
    context ={
        'account_activities': account_activities,
        'title': account_instance.name+' Details',
        'account': account_instance,
        }
    if account_instance.account_type == EXPENSES:
        return render(request, 'accounts/expenses_details.html', context)    
    return render(request, 'accounts/bank_details.html', context)

@login_required
def new_account(request):
    forms = Account_form()
    
    if request.method == 'POST':
        forms = Account_form(request.POST)
        print(request.POST)
        
        if forms.is_valid():
            data = {
                'name': forms.cleaned_data['name'],
                'description': forms.cleaned_data['description'],
                'account_type': forms.cleaned_data['account_type'],
                'opening_balance': forms.cleaned_data['opening_balance'],
                'account_balance': forms.cleaned_data['opening_balance'],
            }
            
            Accounts.objects.create(**data)
            
            messages.success(request, data["name"]+" added to your list of "+data["account_type"]+".")
            return redirect('accounts')
    
    #messages.success(request, "added to your list of .")
    context={
        'form': forms,
        'title': 'New Account',
    }
    return render(request, 'accounts/new.html', context)

@login_required
def edit_account(request, account_id):
    account_instance = Accounts.objects.get(pk=account_id)
    forms = Account_form(request.POST or None, instance=account_instance)
    if request.method == 'POST':
        if forms.is_valid():
            forms.save()
            messages.success(request, 'Account updated successfully.')
            return redirect(get_account, account_id)
    
    context = {
        "title" : "Edit: "+ account_instance.name,
        "account": account_id,
        "form" : forms
    }
    return render(request, 'accounts/edit.html', context)

@login_required
def delete_account(request, account_id):
    account_instance = Accounts.objects.get(pk=account_id)
    
    #get all transactions related to this account.
    
    
    if request.method == 'POST':
        pass
    
    messages.warning(request, 'This action can not be undone. Click delete if you are sure you want to delete this account.')
    context = {
        "title" : "Delete: "+ account_instance.name,
        'account': account_instance,
        'related_transaction_count': 12,
        'related_transactions': 'Deleting this account will alter your accounting. I suggest you reasign all transactions related to this account to another account before deleting.'
    }
    return render(request, 'accounts/delete.html', context)

def calculate_payables():
    sum_total = 0
    people_instance = People.objects.filter(Q(people_type='vendor') & Q(status = 'active'))
    for amount in people_instance:
        sum_total += amount.balance
        
    context={
        'people':people_instance,
        'payable_amount': sum_total
    }
    return context

def calculate_receiveables():
    sum_total = 0
    people_instance = People.objects.filter(Q(people_type='customer') & Q(status = 'active'))
    for amount in people_instance:
        sum_total += amount.balance
        
    context={
        'people':people_instance,
        'payable_amount': sum_total
    }
    return context

@login_required
def receiveables(request):
    
    context={
        'title' : 'Receivables',
        'details' : calculate_receiveables()['people'],
        'amount': calculate_receiveables()['payable_amount']
    }
    
    return render(request, 'accounts/receiveables.html',context)

@login_required
def payables(request):
    
    context={
        'title' : 'Payable',
        'details' : calculate_payables()['people'],
        'amount': calculate_payables()['payable_amount']
    }
    return render(request, 'accounts/payables.html', context)

@login_required
def payments(request):
    payments = Account_activities.objects.all().order_by('-id')
    context ={
        "payments" : payments,
        "title" : "All Payments",
    }
    return render(request, 'payments/index.html',context)

@login_required
def make_payment(request):
    form = Payment_form()
    form.fields["applied_to"].queryset = People.objects.filter(people_type='vendor').filter(status='active')
    form.fields['from_account'].queryset = Accounts.objects.filter(account_type = BANK)
    
    if request.method == "POST":
        form = Payment_form(request.POST)
        if form.is_valid():
            data ={
                'applied_to':People.objects.get(name = form.cleaned_data['applied_to']),
                'description':form.cleaned_data['description'],
                'from_account':Accounts.objects.get(name = form.cleaned_data['from_account']),
                'amount':form.cleaned_data['amount'],
                'payment_type':BILL,
                'applied_by' : request.user,
                'payment_at':form.cleaned_data['payment_at'],
            }
            apply_payment(request, data, from_or_to_account = "from_account")
            Account_activities.objects.create(**data)
            messages.success(request, 'Payment applied successfully.')
            return redirect(payments)
        
    context ={
        "title" : "Pay Vendor",
        'form' : form,
    }
    return render(request, 'payments/make_payment.html', context)

@login_required
def receive_payment(request):
    form = Payment_form()
    form.fields["applied_to"].queryset = People.objects.filter(people_type='customer').filter(status='active')
    form.fields['to_account'].queryset = Accounts.objects.filter(account_type = BANK)
    
    if request.method == "POST":
        form = Payment_form(request.POST)
        print(request.user)
        if form.is_valid():
            
            data ={
                'applied_to':People.objects.get(name = form.cleaned_data['applied_to']),
                'description':form.cleaned_data['description'],
                'to_account':Accounts.objects.get(name = form.cleaned_data['to_account']),
                'amount':form.cleaned_data['amount'],
                'payment_type':SALES,
                'applied_by' : request.user,
                'payment_at':form.cleaned_data['payment_at'],
            }
            
            
            apply_payment(request, data, from_or_to_account = "to_account")
            Account_activities.objects.create(**data)
            messages.success(request, 'Payment applied successfully.')
            return redirect(payments)
        
    context ={
        "title" : "Receive Payment",
        'form' : form,
    }
    return render(request, 'payments/recieve_payment.html', context)

@login_required
def apply_payment(request,data, **kwargs):
    #update  bank balance
    account_instance = data[kwargs['from_or_to_account']]
    if data["payment_type"] == SALES:
        account_balance = Decimal(account_instance.account_balance) + Decimal(data['amount'])
    elif data["payment_type"] == BILL:
        account_balance = Decimal(account_instance.account_balance) - Decimal(data['amount'])
    account_instance.account_balance = Decimal(account_balance)
    account_instance.save()
    
    #update vendor balance and customer balance
    people_instance = data['applied_to']
    balance = people_instance.balance - data['amount']
    people_instance.balance = Decimal(balance)
    people_instance.save()

@login_required   
def make_transfer(request):
    
    context = {
        'title': 'Transfer Fund'
    }
    return render(request, 'payments/transfer.html', context)