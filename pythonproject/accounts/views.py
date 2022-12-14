from datetime import datetime
from decimal import Decimal
from os import name
from turtle import st
from urllib.parse import urlparse
from django.contrib import messages
from django.http import Http404
from django.http import JsonResponse
from django.urls import reverse, resolve
from django.views.generic.base import View
from django.db.models import Sum, F, Q
from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from .models import Accounts, Account_activities
from .forms import (Account_form, Payment_form, Transfer_form, Expenses_form)
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
    def get(self, request, *args, **kwargs):
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
    account_instance = Accounts.objects.get(pk=account_id)
    account_activities = Account_activities.objects.filter(
        Q(to_account=account_id) | Q(from_account=account_id)).order_by('-pk')

    for account_activity in account_activities:
        if account_activity.to_account == account_id:
            account_activities["account"] = account_activity.to_account
        elif account_activity.from_account == account_id:
            account_activities["account"] = account_activity.from_account

    context = {
        'this_bank': account_instance,
        'account_activities': account_activities,
        'title': account_instance.name + ' Details',
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

            messages.success(request, data["name"] + " added to your list of " + data["account_type"] + ".")
            return redirect('accounts')

    # messages.success(request, "added to your list of .")
    context = {
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
        "title": "Edit: " + account_instance.name,
        "account": account_id,
        "form": forms
    }
    return render(request, 'accounts/edit.html', context)


@login_required
def delete_account(request, account_id):
    account_instance = Accounts.objects.get(pk=account_id)

    # get all transactions related to this account.

    if request.method == 'POST':
        pass

    messages.warning(request,
                     'This action can not be undone. Click delete if you are sure you want to delete this account.')
    context = {
        "title": "Delete: " + account_instance.name,
        'account': account_instance,
        'related_transaction_count': 12,
        'related_transactions': 'Deleting this account will alter your accounting. I suggest you reasign all transactions related to this account to another account before deleting.'
    }
    return render(request, 'accounts/delete.html', context)


def calculate_payables():
    sum_total = 0
    people_instance = People.objects.filter(Q(people_type='vendor') & Q(status='active'))
    for amount in people_instance:
        sum_total += amount.balance

    context = {
        'people': people_instance,
        'payable_amount': sum_total
    }
    return context


def calculate_receiveables():
    sum_total = 0
    people_instance = People.objects.filter(Q(people_type='customer') & Q(status='active'))
    for amount in people_instance:
        sum_total += amount.balance

    context = {
        'people': people_instance,
        'payable_amount': sum_total
    }
    return context


@login_required
def receiveables(request):
    context = {
        'title': 'Receivables',
        'details': calculate_receiveables()['people'],
        'amount': calculate_receiveables()['payable_amount']
    }

    return render(request, 'accounts/receiveables.html', context)


@login_required
def payables(request):
    context = {
        'title': 'Payable',
        'details': calculate_payables()['people'],
        'amount': calculate_payables()['payable_amount']
    }
    return render(request, 'accounts/payables.html', context)


@login_required
def payments(request):
    payments = Account_activities.objects.filter(~Q(payment_type=EXPENSES)).order_by('-id')
    context = {
        "payments": payments,
        "title": "All Payments",
    }
    return render(request, 'payments/index.html', context)


@login_required
def get_payments(request, payment_id):
    payments = Account_activities.objects.filter(pk=payment_id)
    context = {
        "payment": payments,
        "title": "Tansaction: #" + str(payment_id),
    }
    return render(request, 'payments/payment.html', context)


@login_required
def make_payment(request):
    form = Payment_form()
    form.fields["applied_to"].queryset = People.objects.filter(people_type='vendor').filter(status='active')
    form.fields['from_account'].queryset = Accounts.objects.filter(account_type=BANK)

    if request.method == "POST":
        form = Payment_form(request.POST)
        if form.is_valid():
            description = 'Bill payment'
            data = {
                'applied_to': People.objects.get(name=form.cleaned_data['applied_to']),
                'description': form.cleaned_data['description'],
                'from_account': Accounts.objects.get(name=form.cleaned_data['from_account']),
                'amount': form.cleaned_data['amount'],
                'payment_type': BILL,
                'applied_by': request.user,
                'created_at': form.cleaned_data['created_at'],
            }
            if data['description'] == None:
                data['description'] = description

            apply_payment(request, data, from_or_to_account="from_account")
            Account_activities.objects.create(**data)
            messages.success(request, 'Payment applied successfully.')
            return redirect(payments)

    context = {
        "title": "Pay Vendor",
        'form': form,
    }
    return render(request, 'payments/make_payment.html', context)


@login_required
def receive_payment(request):
    form = Payment_form()
    form.fields["applied_to"].queryset = People.objects.filter(people_type='customer').filter(status='active')
    form.fields['to_account'].queryset = Accounts.objects.filter(account_type=BANK)

    if request.method == "POST":
        form = Payment_form(request.POST)
        if form.is_valid():
            description = 'Sales payment'

            data = {
                'applied_to': People.objects.get(name=form.cleaned_data['applied_to']),
                'description': form.cleaned_data['description'],
                'to_account': Accounts.objects.get(name=form.cleaned_data['to_account']),
                'amount': form.cleaned_data['amount'],
                'payment_type': SALES,
                'applied_by': request.user,
                'created_at': form.cleaned_data['created_at'],
            }
            if data['description'] == None:
                data['description'] = description

            apply_payment(request, data, from_or_to_account="to_account")
            Account_activities.objects.create(**data)
            messages.success(request, 'Payment applied successfully.')
            return redirect(payments)

    context = {
        "title": "Receive Payment",
        'form': form,
    }
    return render(request, 'payments/recieve_payment.html', context)


@login_required
def edit_payment(request, payment_id):
    payment_instance = Account_activities.objects.get(pk=payment_id)
    form = Payment_form(request.POST or None, instance=payment_instance)
    if payment_instance.payment_type == BILL:
        form.fields["applied_to"].queryset = People.objects.filter(people_type='vendor').filter(status='active')
    elif payment_instance.payment_type == SALES:
        form.fields["applied_to"].queryset = People.objects.filter(people_type='customer').filter(status='active')
    else:
        pass
    form.fields['to_account'].queryset = Accounts.objects.filter(account_type=BANK)

    if request.method == "POST":
        form = Payment_form(request.POST)
        if form.is_valid():
            description = 'Sales payment'

            if payment_instance.payment_type == BILL:
                description = 'Bill payment'

            data = {
                'applied_to': People.objects.get(name=form.cleaned_data['applied_to']),
                'description': form.cleaned_data['description'],
                'amount': form.cleaned_data['amount'],
                'created_at': form.cleaned_data['created_at'],
                'payment_type': payment_instance.payment_type,
            }
            if payment_instance.payment_type == BILL:
                data['from_account'] = form.cleaned_data['from_account']
            if payment_instance.payment_type == SALES:
                data['to_account'] = form.cleaned_data['to_account']

            if data['description'] == None:
                data['description'] = description

            if payment_instance.payment_type == SALES:
                print('sales updated!!')

                reverse_applied_payment(request, data, payment_instance.amount, from_or_to_account="to_account")
                apply_payment(request, data, from_or_to_account="to_account")
            elif payment_instance.payment_type == BILL:
                print('bills updated!!')
                reverse_applied_payment(request, data, payment_instance.amount, from_or_to_account="from_account")
                apply_payment(request, data, from_or_to_account="from_account")

            Account_activities.objects.filter(pk=payment_id).update(**data)
            messages.success(request, 'Payment updated successfully.')
            return redirect(payments)

    context = {
        "title": "Edit Payment #" + str(payment_id),
        'form': form,
    }
    if payment_instance.payment_type == BILL:
        return render(request, 'payments/make_payment.html', context)
    return render(request, 'payments/recieve_payment.html', context)


@login_required
def apply_payment(request, data, **kwargs):
    # update  bank balance
    account_instance = data[kwargs['from_or_to_account']]
    if data["payment_type"] == SALES:
        account_balance = Decimal(account_instance.account_balance) + Decimal(data['amount'])
    elif data["payment_type"] == BILL:
        account_balance = Decimal(account_instance.account_balance) - Decimal(data['amount'])
    account_instance.account_balance = Decimal(account_balance)
    account_instance.save()

    # update vendor balance and customer balance
    people_instance = data['applied_to']
    balance = people_instance.balance - data['amount']
    people_instance.balance = Decimal(balance)
    people_instance.save()


def reverse_applied_payment(request, data, amount, **kwargs):
    # update  bank balance
    account_instance = data[kwargs['from_or_to_account']]
    if data["payment_type"] == SALES:
        account_balance = Decimal(account_instance.account_balance) - Decimal(amount)
    elif data["payment_type"] == BILL:
        account_balance = Decimal(account_instance.account_balance) + Decimal(amount)
    account_instance.account_balance = Decimal(account_balance)
    account_instance.save()

    # update vendor balance and customer balance
    people_instance = data['applied_to']
    balance = people_instance.balance + amount
    people_instance.balance = Decimal(balance)
    people_instance.save()


@login_required
def make_transfer(request):
    transfer_form = Transfer_form()
    transfer_form.fields['to_account'].queryset = Accounts.objects.filter(account_type=BANK)
    transfer_form.fields['from_account'].queryset = Accounts.objects.filter(account_type=BANK)

    if request.method == 'POST':
        form = Transfer_form(request.POST or None)
        if form.is_valid():
            data = {
                'description': "Fund Transfer",
                'to_account': Accounts.objects.get(name=form.cleaned_data['to_account']),
                'from_account': Accounts.objects.get(name=form.cleaned_data['from_account']),
                'amount': form.cleaned_data['amount'],
                'payment_type': TRF,
                'applied_by': request.user,
                'created_at': form.cleaned_data['created_at'],
            }

            if data['to_account'] != data['from_account']:
                Account_activities.objects.create(**data)
                update_transfer_account(data)
                messages.success(request, 'Fund transfered successfully.')
                redirect(payments)
            else:
                messages.error(request,
                               'You are trying to transfer fund to the same account. please choose another account to transfer fund to.')
    context = {
        'title': 'Transfer Fund',
        'form': transfer_form
    }
    return render(request, 'payments/transfer.html', context)


def update_transfer_account(data):
    to_account_balance = Accounts.objects.get(pk=data['to_account'].id)
    from_account_balance = Accounts.objects.get(pk=data['from_account'].id)
    to_balance = to_account_balance.account_balance + data['amount']
    from_balance = from_account_balance.account_balance - data['amount']

    to_account_balance.account_balance = to_balance
    to_account_balance.save()

    from_account_balance.account_balance = from_balance
    from_account_balance.save()


def reverse_transfer(transfer_instance):
    old_from_bank = Accounts.objects.get(name=transfer_instance.from_account)
    old_from_bank.account_balance = old_from_bank.account_balance + transfer_instance.amount
    old_from_bank.save()
    old_to_bank = Accounts.objects.get(name=transfer_instance.to_account)
    old_to_bank.account_balance = old_to_bank.account_balance - transfer_instance.amount
    old_to_bank.save()


@login_required
def edit_transfer(request, transfer_id):
    transfer_instance = Account_activities.objects.get(pk=transfer_id)

    transfer_form = Transfer_form(instance=transfer_instance)

    transfer_form.fields['to_account'].queryset = Accounts.objects.filter(account_type=BANK)
    transfer_form.fields['from_account'].queryset = Accounts.objects.filter(account_type=BANK)

    current_transfer_amount = transfer_instance.amount

    if request.method == 'POST':
        form = Transfer_form(request.POST or None)

        if form.is_valid():
            data = {
                'description': "Fund Transfer",
                'to_account': Accounts.objects.get(name=form.cleaned_data['to_account']),
                'from_account': Accounts.objects.get(name=form.cleaned_data['from_account']),
                'amount': form.cleaned_data['amount'],
                'payment_type': TRF,
                'applied_by': request.user,
                'created_at': form.cleaned_data['created_at'],
            }

            if data['to_account'] != data['from_account']:
                if data['to_account'] == transfer_instance.to_account and data[
                    'from_account'] == transfer_instance.from_account:
                    data['from_account'].account_balance = data['from_account'].account_balance + (
                                current_transfer_amount - data['amount'])
                    data['to_account'].account_balance = data['to_account'].account_balance - current_transfer_amount + \
                                                         data['amount']
                    data['from_account'].save()
                    data['to_account'].save()

                else:
                    # revarse the old amount transfered to the account.
                    reverse_transfer(transfer_instance)
                    update_transfer_account(data)

                Account_activities.objects.filter(pk=transfer_id).update(**data)
                messages.success(request, 'Fund transfered successfully.')
                return redirect(payments)
            else:
                messages.error(request,
                               'You are trying to transfer fund to the same account. please choose another account to transfer fund to.')
                return redirect(payments)
    context = {
        'title': 'Transfer Fund',
        'form': transfer_form
    }
    return render(request, 'payments/transfer.html', context)


@login_required
def get_transaction_details(request, transaction_id):
    details = Account_activities.objects.get(pk=transaction_id)
    if details.payment_type == 'TRF':
        edit_link = 'edit_transfer'
        back_link = 'payments'
        title2 = 'FUND TRANSFER'
    elif details.payment_type == 'expenses':
        edit_link = 'edit_expenses'
        back_link = 'expenses'
        title2 = 'EXPENSES'
    elif details.payment_type == 'bill':
        edit_link = "edit_payment"
        back_link = 'payments'
        title2 = 'BILL PAYMENT'
    else:
        edit_link = "edit_payment"
        title2 = 'SALES PAYMENT'
        back_link = 'payments'
    context = {
        "title": "Transaction #" + str(transaction_id),
        "transaction": details,
        'edit_link': edit_link,
        'back_link': back_link,
        'heading': title2,
    }
    return render(request, 'payments/payment.html', context)


@login_required
def expenses(request):
    payments = Account_activities.objects.filter(payment_type=EXPENSES).order_by('-id')
    context = {
        "payments": payments,
        "title": "All Expenses",
    }
    return render(request, 'payments/expenses.html', context)


@login_required
def get_expenses(request, id):
    payments = Account_activities.objects.filter(payment_type=EXPENSES).order_by('-id')
    context = {
        "payments": payments,
        "title": "All Expenses",
    }
    return render(request, 'payments/expenses.html', context)


@login_required
def new_expenses(request):
    expenses_form = Expenses_form()
    expenses_form.fields['to_account'].queryset = Accounts.objects.filter(account_type=EXPENSES)
    expenses_form.fields['from_account'].queryset = Accounts.objects.filter(account_type=BANK)

    if request.method == 'POST':

        form = Expenses_form(request.POST or None)
        if form.is_valid():
            data = {
                'description': form.cleaned_data['description'],
                'to_account': Accounts.objects.get(name=form.cleaned_data['to_account']),
                'from_account': Accounts.objects.get(name=form.cleaned_data['from_account']),
                'amount': form.cleaned_data['amount'],
                'payment_type': EXPENSES,
                'applied_by': request.user,
                'created_at': form.cleaned_data['created_at'],
            }

            data['from_account'].account_balance = data['from_account'].account_balance - data['amount']
            data['from_account'].save()

            Account_activities.objects.create(**data)

            messages.success(request, 'Expense recored successfully')
            redirect(expenses)

    context = {
        'title': "New Expenses",
        'form': expenses_form,
    }
    return render(request, 'payments/new_expenses.html', context)


def reverse_expenses(details):
    old_bank = Accounts.objects.get(name=details.from_account)
    old_bank.account_balance = old_bank.account_balance + details.amount
    old_bank.save()


@login_required
def edit_expenses(request, expenses_id):
    expenses_instance = Account_activities.objects.get(pk=expenses_id)

    expenses_form = Expenses_form(instance=expenses_instance)
    expenses_form.fields['to_account'].queryset = Accounts.objects.filter(account_type=EXPENSES)
    expenses_form.fields['from_account'].queryset = Accounts.objects.filter(account_type=BANK)

    current_expense_amount = expenses_instance.amount
    current_expense_bank = expenses_instance.from_account

    if request.method == 'POST':

        form = Expenses_form(request.POST or None)
        if form.is_valid():
            data = {
                'description': form.cleaned_data['description'],
                'to_account': Accounts.objects.get(name=form.cleaned_data['to_account']),
                'from_account': Accounts.objects.get(name=form.cleaned_data['from_account']),
                'amount': form.cleaned_data['amount'],
                'payment_type': EXPENSES,
                'applied_by': request.user,
                'created_at': form.cleaned_data['created_at'],
            }

            if current_expense_bank == data['from_account']:
                data['from_account'].account_balance = data['from_account'].account_balance + current_expense_amount - \
                                                       data['amount']
            else:
                # return the amount to the previous account
                reverse_expenses(expenses_instance)
                data['from_account'].account_balance = data['from_account'].account_balance - data['amount']

            data['from_account'].save()

            Account_activities.objects.filter(pk=expenses_id).update(**data)

            messages.success(request, 'Expense updated successfully')
            return redirect(expenses)

    context = {
        'title': "Edit Expenses",
        'form': expenses_form,
    }
    return render(request, 'payments/new_expenses.html', context)


def delete_transaction(request, transaction_id):
    details = Account_activities.objects.get(pk=transaction_id)
    if details.payment_type == 'TRF':
        back_link = 'payments'
        title2 = 'FUND TRANSFER'
    elif details.payment_type == 'expenses':
        back_link = 'expenses'
        title2 = 'EXPENSES'
    elif details.payment_type == 'bill':
        back_link = 'payments'
        title2 = 'BILL PAYMENT'
    else:
        title2 = 'SALES PAYMENT'
        back_link = 'payments'

    if request.method == "POST":
        data = {
            'from_account': details.from_account,
            'to_account': details.to_account,
            'payment_type': details.payment_type,
            'applied_to': details.applied_to
        }
        if details.payment_type == EXPENSES:
            # return the amount to the previous account
            reverse_expenses(details)
        elif details.payment_type == TRF:
            reverse_transfer(details)
        elif details.payment_type == SALES:
            reverse_applied_payment(request, data, details.amount, from_or_to_account='to_account')
        elif details.payment_type == BILL:
            reverse_applied_payment(request, data, details.amount, from_or_to_account='from_account')
        else:
            pass

        Account_activities.objects.filter(pk=transaction_id).delete()
        messages.success(request, 'Transaction deleted successfully.')
        return redirect(back_link)
    messages.warning(request, 'Note: This action can not be undone. ARE YOU SURE YOU WANT TO CONTINUE ?')

    context = {
        "title": "Delete Transaction #" + str(transaction_id),
        "transaction": details,
        'back_link': back_link,
        'heading': title2,
    }
    return render(request, 'payments/delete.html', context)