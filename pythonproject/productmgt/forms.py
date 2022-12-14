from django import forms
from django.forms import formset_factory
from .models import (InvoiceActivities, Products, Invoice, People, Accounts)

class product_form(forms.ModelForm):
    class Meta:
        model = Products
        fields = ["name",'brand',"opening_stock","cost_price","selling_price","description","reorder_point"]
    
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control form-control-lg',
        'placeholder': "Product Name",
        'id': "name",
    }))
    brand = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder': "Product Brand",
        'id': "brand",
    }))
    opening_stock = forms.DecimalField(required=False,widget=forms.NumberInput(attrs={
        'class':'form-control',
        'placeholder': "Quantity in stock as at today",
        'id': "opening_stock",
    }),error_messages={'required':'Please enter your opening stock.'})
    
    cost_price = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class':'form-control',
        'placeholder': "Price of purchasing the product",
        'id': "cost_price",
    }))
    selling_price = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class':'form-control',
        'placeholder': "Selleing price",
        'id': "selling_price",
    }))
    reorder_point = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class':'form-control',
        'placeholder': "Level to replanish your stock",
        'id': "reorder_point",
        'required': False
    }))
    description = forms.CharField(widget=forms.Textarea(attrs={
        'class':'form-control',
        'placeholder': "Description of the product",
        'id': "description",
    }))
    
class people_form(forms.ModelForm):
    class Meta:
        model = People
        fields = ["name",'balance',"email","phone","address","people_type","status"]
    
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control form-control-lg',
        'placeholder': "Business or Personl Name",
        'id': "name",
    }),error_messages={'required':'Please enter name.'})
    balance = forms.CharField(required=False,widget=forms.NumberInput(attrs={
        'class':'form-control',
        'placeholder': "Current Balance",
        'id': "balance",
    }))
    email = forms.EmailField(required=False,widget=forms.EmailInput(attrs={
        'class':'form-control',
        'placeholder': "Email Address",
        'id': "email",
    }))
    
    phone = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder': "Phone Number",
        'id': "phone",
    }))
    STATUS_CHOICE=(
        ("disabled","Disabled"),
        ("active", "Active")
    )
    status = forms.ChoiceField(choices= STATUS_CHOICE,required=False)
    status.widget.attrs.update({
        'class': "form-control",
        'id': "status",
    })
    TYPE_CHOICE=[
        ("customer", "Customer"),
        ("vendor","Vendor"),
    ]
    people_type = forms.ChoiceField(choices=TYPE_CHOICE, required=False)
    people_type.widget.attrs.update({    
        'class':'form-control',
        'id': "people_type",
    })
    
    address = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder': "Contact Address",
        'id': "address",
    }))
    
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'people',
            #'invoice_at',
            'created_at',
        ]
        widgets = {
            'people': forms.Select(attrs={
                'class': 'form-control select2',
                'id': 'customer-name',
                'name': 'people',
            }),
            ''' 'invoice_at': forms.DateInput(attrs={
                'class': 'form-control',
                'id': 'invoice_at',
                'placeholder': 'Enter date create',
                'type': 'date',
                'name': 'invoice_at',
            }),'''
            'created_at': forms.DateInput(attrs={
                'class': 'form-control',
                'id': 'created_at',
                'placeholder': 'Enter date create',
                'type': 'date',
                'name': 'created_at',
            }),
        }
        
class InvoiceDetailsForm(forms.ModelForm):
    class Meta:
        model = InvoiceActivities
        fields = [
            'products',
            'price',
            'quantity',
        ]
        widgets = {
            'products': forms.Select(attrs={
                'class': 'form-control-sm select2 invoice-product',
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'form-control-sm invoice-quantity',
                'placeholder': 'quantity',
                'type': 'number',
            }),
            'price': forms.TextInput(attrs={
                'class': 'form-control-sm invoice-price',
                'placeholder': 'price',
                'type': 'number',
            })
        }


InvoiceDetailsFormSet = formset_factory(InvoiceDetailsForm, extra=8)
    
    