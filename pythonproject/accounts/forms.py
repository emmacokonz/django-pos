from django import forms
from django.forms import formset_factory
from .models import (Accounts, Account_activities)

class Account_form(forms.ModelForm):
    class Meta:
        model = Accounts
        fields = [
            "name",
            'description',
            "opening_balance",
            "account_type",
            "opening_balance_at"
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'account-name',
                'required':'required',
                'name': 'name',
                'placeholder': 'Account Name'
            }),
            
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'description',
                'name': 'description',
                'placeholder': 'description of this account.',
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'opening-balance',
                'name': 'opening_balance',
                'placeholder': '0.00'
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-control select2',
                'id': 'account-type',
                'name': 'account_type',
            }),
            'opening_balance_at': forms.DateInput(attrs={
                'class': 'form-control',
                'id': 'opening-balance-at',
                'type':'date',
                'name': 'opening_balance_at',
            }),
        }

class Payment_form(forms.ModelForm):
    class Meta:
        model = Account_activities
        fields = [
            "applied_to",
            'description',
            "amount",
            "payment_at",
            "to_account",
            'from_account',
            "payment_type"
        ]
        widgets = {
            'applied_to': forms.Select(attrs={
                'class': 'form-control select2',
                'required':'required',
                'name': 'applied_to',
            }),
            
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'description',
                'name': 'description',
                'placeholder': 'description for the payment.',
            }),
            'payment_at': forms.DateInput(attrs={
                'class': 'form-control',
                'name': 'payment_at',
                'type':'date',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'name': 'amount',
            }),
            'to_account': forms.Select(attrs={
                'class': 'form-control select2',
                'name': 'to_account',
            }),
            
            'from_account': forms.Select(attrs={
                'class': 'form-control select2',
                'name': 'from_account',
            }),
            
            'payment_type': forms.Select(attrs={
                'class': 'form-control',
                'name': 'payment_type',
            }),
        }
