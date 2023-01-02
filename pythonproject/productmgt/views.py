import json
from datetime import datetime
from decimal import Decimal
from os import name
from turtle import st
from itertools import chain
from operator import attrgetter
from urllib.parse import urlparse
from django.contrib import messages
from django.http import Http404
from django.http import JsonResponse
from django.urls import reverse,resolve
from django.db.models import Sum,F,Q
from django.shortcuts import render,redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from .forms import (InvoiceDetailsForm, InvoiceDetailsFormSet, InvoiceForm, product_form, people_form)
from django.forms import inlineformset_factory
from .models import (Products, Invoice, People, InvoiceActivities, )
from accounts.models import (Account_activities, Accounts)


# Create your views here.
@login_required
def productsList(request):
    products = get_list_or_404(Products)
    if products:
        for eachProduct in products:
            eachProduct.progress = product_progress(qty_in_stock=eachProduct.quantity, reorder_point=eachProduct.reorder_point)
    context = {
        "products": products,
        'title': 'Product List'
    }
    return render(request, 'products/index.html', context)

@login_required
def productDetails(request, product_code):
    thisProduct = get_product_details(product_code)
    invActivities = InvoiceActivities.objects.filter(products_id= thisProduct.id)
    for tt in invActivities:
        tt.amount = tt.price * tt.quantity
        tt.type = get_invoice_details_by_id(tt.invoice_no_id).invoice_type
    
    context = {
        "product": thisProduct,
        'product_activities': invActivities,
        "title" : "Details about "+ thisProduct.name,
        }
    return render(request, 'products/details.html', context)

@login_required
def new_product(request):
    forms = product_form()
    if request.method == 'POST':
        forms = product_form(request.POST)
        if forms.is_valid():
            data= {
                'name': forms.cleaned_data["name"],
                'brand': forms.cleaned_data["brand"],
                'opening_stock': forms.cleaned_data["opening_stock"],
                'cost_price': forms.cleaned_data["cost_price"],
                "selling_price": forms.cleaned_data["selling_price"],
                "reorder_point": forms.cleaned_data["reorder_point"],
                "quantity": forms.cleaned_data["opening_stock"],
                "description": forms.cleaned_data["description"],
                "product_code": generate_product_code(),
                'created_by_id': request.user.id,
                'status' : 'in stock'
            }
            if data['quantity'] == 0:
                data['status'] = 'out of stock'
                
            Products.objects.create(**data)
            messages.success(request, data['name']+" Added to your list of products.")
            return redirect(productsList)
            
    context = {
        'form' : forms,
        "title" : "Product Creation ",
        }
    return render(request,'products/new.html', context)

@login_required
def edit_product(request, product_code):
    thisProduct1 = get_product_details(product_code)
    #thisProduct1 =Products.objects.get(pk=thisProductss.id)
    
    forms = product_form(request.POST or None, instance=thisProduct1)
    
    if request.method == "POST":
        if forms.is_valid():
            if forms.has_changed:
                forms.save()
                messages.success(request, "Product update was successful.")
                
            return redirect(productsList)
            
    context={
        'form': forms,
        'title': 'Edit '+thisProduct1.name,
        'product': thisProduct1
    }
    return render(request,'products/edit.html', context)

@login_required
def delete_product(request, product_code):
    
    product = get_product_details(product_code)
    
    activity = InvoiceActivities.objects.filter(products_id = product.id)
    if activity :
        if product.status != 'disabled':
            messages.info(request, "This product can\'t be deleted, because invoice is attached to it. But you can disable the product by clicking view.")
        else:
            messages.info(request, 'This product can\'t be deleted, because invoice is attached to it.')
        return redirect(productsList)
    #product.delete()
    messages.success(request, 'Product deleted.')
    
    return redirect(productsList)

@login_required
def enable_product(request, product_code):
    qty = get_product_details(product_code).quantity
    
    if qty > 0 :
        Products.objects.filter(product_code=product_code).update(status = 'in-stock')
    else:
        Products.objects.filter(product_code=product_code).update(status = 'out-of-stock')
        
    messages.success(request, 'Product Activivated and ready for invoicing.')
    return redirect('product_details', product_code=product_code)
    
@login_required
def disable_product(request, product_code):
    Products.objects.filter(product_code=product_code).update(status = 'disabled')
        
    messages.warning(request, 'Product deactivated and will not be available for invoicing untill you activate it.')
    return redirect('product_details', product_code=product_code)
    
@login_required
def people(request):
    people=People.objects.all().order_by("id")
    payments = Account_activities.objects.filter(Q(payment_type='sales') | Q(payment_type = 'bill')).order_by("id")
    invoices = Invoice.objects.all().order_by("id")
    result_list =  sorted(chain(payments,invoices),reverse=True,key=attrgetter('created_at'))
    
    context={
        "people":people,
        'title': 'People',
        'transactions': result_list
    }
    return render(request,'people/index.html',context)

@login_required
def peopleDetails(request, people_id):
    person = People.objects.get(pk=people_id)
    payments = Account_activities.objects.filter(Q(Q(payment_type='sales') | Q(payment_type = 'bill')) and Q(applied_to = person)).order_by("id")
    invoices = Invoice.objects.filter(people = person).order_by("id")
    result_list =  sorted(chain(payments,invoices),reverse=True,key=attrgetter('created_at'))
    
    context={
        'person':person,
        'title': 'Details about  '+person.name,
        'transactions': result_list,
    }
    if person.status == 'disabled':
        messages.warning(request, person.name+' is deactivated and will not be available for invoicing and payments untill you activate it.')
    return render(request,'people/details.html',context)

@login_required
def new_people(request):
    forms = people_form()
    
    if request.method == "POST":
        forms = people_form(request.POST)
        if forms.is_valid():
            data = {
                'name' : forms.cleaned_data['name'],
                'email': forms.cleaned_data['email'],
                "phone" : forms.cleaned_data['phone'],
                "people_type":forms.cleaned_data['people_type'],
                "status": forms.cleaned_data['status'],
                "address": forms.cleaned_data['address'],
                "balance": forms.cleaned_data['balance'],
            }
            People.objects.create(**data)
            
            messages.success(request, data["name"]+" added to your list of "+data["people_type"]+".")
            return redirect(people)
            
        
    context={
        "form": forms,
        'title': 'Create People'
    }
    return render(request,'people/new.html',context)

@login_required
def edit_people(request,people_id):
    instance = People.objects.get(pk=people_id)
    forms = people_form(request.POST or None,instance=instance)
    if request.method == 'POST':
        if forms.is_valid():
            forms.save()
            messages.success(request, instance.people_type+" updated successfully")
            return redirect(peopleDetails, people_id)
        else:
            messages.error(request, forms.errors)
    context={
        'person':instance,
        "form": forms,
        "title": 'Edit '+instance.name+' Details'
    }
    
    return render(request,'people/edit.html',context)

@login_required
def enable_people(request, people_id):
    person = People.objects.get(pk = people_id)
    People.objects.filter(pk=people_id).update(status = 'active')
        
    messages.success(request, person.name+' activation was successful.')
    return redirect(peopleDetails, people_id)
    
@login_required
def disable_people(request, people_id):
    person = People.objects.get(pk = people_id)
    People.objects.filter(pk=people_id).update(status = 'disabled')
        
    #messages.warning(request, person.name+'is  deactivated and will not be available for invoicing and payments untill you activate it.')
    return redirect(peopleDetails, people_id)
    
    


@login_required
def invoice(request):
    invoices = Invoice.objects.select_related().filter(Q(invoice_type = 'sales') | Q(invoice_type = 'sales_return')).order_by('-created_at')
    
    context={
        "invoices": invoices,
        'title':"Invoice",
    }
    return render(request,'invoice/index.html', context)

@login_required
def invoiceDetails(request, invoice_no):
    invoice = Invoice.objects.get(invoice_no = invoice_no)
   
    details = InvoiceActivities.objects.select_related('products').filter(invoice_no_id=invoice.pk).annotate(amount=F("price")*F('quantity'))
    
    context={
        'invoice_meta': invoice,
        'subtotal': invoice.invoice_amount,
        'details': details,
        "title": invoice.invoice_no,
    }
    return render(request, "invoice/details.html", context)

@login_required
def create_invoice(request):
    form = InvoiceForm()
    form.fields["people"].queryset = People.objects.filter(people_type='customer').filter(status='active')
    formset = InvoiceDetailsFormSet()
    for forms in formset:
        forms.fields["products"].queryset = Products.objects.filter(Q(status='in-stock') | Q(status='out-of-stock'))
    
    context = {
        "form": form,
        'formset': formset,
        'title': 'Create Invoice',
    }
    return render(request, "invoice/create.html",context)

@login_required
def edit_invoice(request, invoice_no):
    context={}
    form_len = 8
    invoice_instance = Invoice.objects.get(invoice_no = invoice_no)
    form = InvoiceForm(request.POST or None, instance=invoice_instance)
    form.fields["people"].queryset = People.objects.filter(people_type='customer').filter(status='active')
    
    invoice_products = InvoiceActivities.objects.filter(invoice_no_id = invoice_instance.pk)
    if len(invoice_products) > form_len:
        form_len = len(invoice_products) + form_len
    else:
        form_len = form_len - len(invoice_products)
        
    ProductFormset = inlineformset_factory(Invoice, InvoiceActivities, form=InvoiceDetailsForm, extra=form_len, can_delete=True)
    formset = ProductFormset(instance=invoice_instance, prefix='invoice')
    #print(formset)
    if request.method == 'POST':
        #print(request.POST)
        formset = ProductFormset(request.POST, instance=invoice_instance, prefix='invoice')
        old_people = invoice_instance.people
        if form.is_valid() and formset.is_valid():
            formdata = form.cleaned_data
            invoice_amount = 0
            invoice_quantity = 0
            people_by_form = People.objects.get(name = formdata['people'])
            
            #update products quantity prviously in the invoice
            for invoice_product in invoice_products:
                
                #update_product_quantity_before_delete(invoice_product).save()
                current_product = Products.objects.get(pk = invoice_product.products.id)
                print('current product quantity: ', current_product.quantity)
                old_product_quantity = current_product.quantity + invoice_product.quantity
                current_product.quantity = old_product_quantity
                print('old product quantity: ', old_product_quantity)
                current_product.save()
                
            invoice_products.delete() #delete previous products in the invoice
            for products in formset:
                
                prod = products.cleaned_data
                if prod.get("products") is not None:
                    invoice_amount += float(prod.get("price") * prod.get("quantity"))
                    invoice_quantity += float(prod.get("quantity"))
                    print('invoice Amount:', invoice_amount)
                    
                    data = {
                        'products': prod.get('products'),
                        'price': prod.get('price'),
                        'quantity': prod.get('quantity'),
                        'invoiced_at': invoice_instance.invoice_at,
                        'invoice_no': invoice_instance
                    }
                    InvoiceActivities.objects.create(**data)
                    
                    #update product quantity
                    product = Products.objects.get(pk = data['products'].id)
                    quantity = product.quantity - data['quantity']
                    product.quantity = quantity
                    print('new product quantity: ', quantity)
                    product.save()
            
            #update user balance
            if old_people.name == formdata['people'].name:
                old_balance = invoice_instance.people.balance - invoice_instance.invoice_amount
                balance = float(old_balance) + float(invoice_amount)
            else:
                old_balance = old_people.balance - invoice_instance.invoice_amount
                old_balance = {'balance': old_balance}
                People.objects.filter(name = old_people.name).update(**old_balance)
                balance = float(people_by_form.balance) + float(invoice_amount)
            print("balance: ", balance)
            new_balance_update={'balance':balance}
            People.objects.filter(name = formdata['people']).update(**new_balance_update)
                
            #update invoice 
            data ={'total_quantity':invoice_quantity, 'invoice_amount':invoice_amount, 'people':people_by_form}
            Invoice.objects.filter(invoice_no = invoice_no).update(**data)
            
            #update invoice actitvities
            
            #update product quantity
            messages.success(request, 'Update was susseccful')
            return redirect('invoice')
        else:
            messages.error(request, 'Unknown error happened!.') 
            
            
    context = {
        "form": form ,
        'formset': formset,
        'title': 'Edit: '+ invoice_no,
        'invoice': invoice_instance,
    }
    return render(request, "invoice/edit.html",context)

@login_required
def update_product_quantity_before_delete(product_instance):
    
    current_product = Products.objects.get(pk = product_instance.products.id)
    print('current product quantity: ', current_product.quantity)
    old_product_quantity = current_product.quantity + product_instance.quantity
    current_product.quantity = old_product_quantity
    print('old product quantity: ', old_product_quantity)
    
    return current_product

@login_required
def delete_invoice(request, invoice_no):
    context ={}
    invoice_instance = Invoice.objects.get(invoice_no = invoice_no)
    
    invoice_products = InvoiceActivities.objects.select_related('products').filter(invoice_no_id=invoice_instance.pk).annotate(amount=F("price")*F('quantity'))
    
    #invoice_products = InvoiceActivities.objects.filter(invoice_no_id = invoice_instance.pk)
    if request.method == 'POST':
        
        # update customer account balance.
        old_balance = invoice_instance.people.balance - invoice_instance.invoice_amount
        balance = {'balance':old_balance}
        print('balance: ',old_balance)
        
        People.objects.filter(pk = invoice_instance.people.id).update(**balance)
        
        #update each product quantity.
        for product in invoice_products:   
            current_product = Products.objects.get(pk = product.products.id)
            print('current product quantity: ', current_product.quantity)
            old_product_quantity = current_product.quantity + product.quantity
            current_product.quantity = old_product_quantity
            print('old product quantity: ', old_product_quantity)
            current_product.save() 
            #update_product_quantity_before_delete(product).save()
            product.delete()
            
        # delete the invoice and the products.
        invoice_instance.delete()
        messages.success(request, 'Invoice deleted successfully')
    
        return redirect('invoice')
    
    messages.warning(request, 'Note: This action can not be undone. ARE YOU SURE YOU WANT TO CONTINUE ?')
    context={
        "title": "Delete: "+invoice_no,
        'invoice_meta': invoice_instance,
        'subtotal': invoice_instance.invoice_amount,
        'details': invoice_products
    }
    return render(request, 'invoice/delete.html',context)

@login_required
def print_invoice(request, invoice_no):
    invoice = Invoice.objects.get(invoice_no = invoice_no)
   
    details = InvoiceActivities.objects.select_related('products').filter(invoice_no_id=invoice.pk).annotate(amount=F("price")*F('quantity'))
    
    context={
        'invoice_meta': invoice,
        'subtotal': invoice.invoice_amount,
        'details': details,
        "title": invoice.invoice_no,
    }
    
    return render(request, "invoice/print.html", context)
    
@login_required
def purchase(request):
    
    invoices = Invoice.objects.select_related().filter(Q(invoice_type = 'purchase') | Q(invoice_type = 'purchase_return')).order_by('-created_at')
    
    context={
        "purchases": invoices,
        'title':"Purchases",
    }

    return render(request,'purchase/index.html',context)

@login_required
def create_purchase(request):
    form = InvoiceForm()
    form.fields["people"].queryset = People.objects.filter(people_type='vendor').filter(status='active')
    formset = InvoiceDetailsFormSet()
    for forms in formset:
        forms.fields["products"].queryset = Products.objects.filter(Q(status='in-stock') | Q(status='out-of-stock'))
    
    context = {
        "form": form,
        'formset': formset,
        'title': 'Create Purchase',
    }
    return render(request, "purchase/create.html",context)

@login_required
def purchaseDetails(request, purchase_no):
    purchase = Invoice.objects.get(invoice_no = purchase_no)
   
    details = InvoiceActivities.objects.select_related('products').filter(invoice_no_id=purchase.pk).annotate(amount=F("price")*F('quantity'))
    
    context={
        'invoice_meta': purchase,
        'subtotal': purchase.invoice_amount,
        'details': details,
        "title": purchase.invoice_no,
    }
    return render(request, "purchase/details.html", context)

@login_required
def edit_purchase(request, invoice_no):
    context={}
    form_len = 8
    invoice_instance = Invoice.objects.get(invoice_no = invoice_no)
    form = InvoiceForm(request.POST or None, instance=invoice_instance)
    form.fields["people"].queryset = People.objects.filter(people_type='vendor').filter(status='active')
    
    invoice_products = InvoiceActivities.objects.filter(invoice_no_id = invoice_instance.pk)
    if len(invoice_products) > form_len:
        form_len = len(invoice_products) + form_len
    else:
        form_len = form_len - len(invoice_products)
        
    ProductFormset = inlineformset_factory(Invoice, InvoiceActivities, form=InvoiceDetailsForm, extra=form_len, can_delete=True)
    formset = ProductFormset(instance=invoice_instance, prefix='purchase')
    
    if request.method == 'POST':
        formset = ProductFormset(request.POST, instance=invoice_instance, prefix='purchase')
        old_people = invoice_instance.people
        if form.is_valid() and formset.is_valid():
            formdata = form.cleaned_data
            invoice_amount = 0
            invoice_quantity = 0
            people_by_form = People.objects.get(name = formdata['people'])
            
            #update products quantity prviously in the invoice
            for invoice_product in invoice_products:
                
                #update_product_quantity_before_delete(invoice_product).save()
                current_product = Products.objects.get(pk = invoice_product.products.id)
                old_product_quantity = current_product.quantity - invoice_product.quantity
                current_product.quantity = old_product_quantity
                current_product.save()
                
            invoice_products.delete() #delete previous products in the invoice
            for products in formset:
                
                prod = products.cleaned_data
                if prod.get("products") is not None:
                    invoice_amount += float(prod.get("price") * prod.get("quantity"))
                    invoice_quantity += float(prod.get("quantity"))
                    
                    data = {
                        'products': prod.get('products'),
                        'price': prod.get('price'),
                        'quantity': prod.get('quantity'),
                        'invoiced_at': invoice_instance.invoice_at,
                        'invoice_no': invoice_instance
                    }
                    InvoiceActivities.objects.create(**data)
                    
                    #update product quantity
                    product = Products.objects.get(pk = data['products'].id)
                    quantity = product.quantity + data['quantity']
                    product.quantity = quantity
                    product.save()
            
            #update user balance
            if old_people.name == formdata['people'].name:
                old_balance = invoice_instance.people.balance - invoice_instance.invoice_amount
                balance = float(old_balance) + float(invoice_amount)
            else:
                old_balance = old_people.balance - invoice_instance.invoice_amount
                People.objects.filter(name = old_people.name).update(**old_balance)
                balance = float(people_by_form.balance) + float(invoice_amount)
            new_balance_update={'balance':balance}
            People.objects.filter(name = formdata['people']).update(**new_balance_update)
                
            #update invoice 
            data ={'total_quantity':invoice_quantity, 'invoice_amount':invoice_amount, 'people':people_by_form}
            Invoice.objects.filter(invoice_no = invoice_no).update(**data)
            
            #update invoice actitvities
            
            #update product quantity
            messages.success(request, 'Update was susseccful')
            return redirect('purchase')
        else:
            messages.error(request, 'Unknown error happened!.') 
            
            
    context = {
        "form": form ,
        'formset': formset,
        'title': 'Edit: '+ invoice_no,
        'invoice': invoice_instance,
    }
    return render(request, "purchase/edit.html",context)


@login_required
def delete_purchase(request, purchase_no):
    context ={}
    purchase_instance = Invoice.objects.get(invoice_no = purchase_no)
    
    invoice_products = InvoiceActivities.objects.select_related('products').filter(invoice_no_id=purchase_instance.pk).annotate(amount=F("price")*F('quantity'))
    
    if request.method == 'POST':
        
        # update customer account balance.
        old_balance = purchase_instance.people.balance - purchase_instance.invoice_amount
        balance = {'balance':old_balance}
        print('balance: ',old_balance)
        
        People.objects.filter(pk = purchase_instance.people.id).update(**balance)
        
        #update each product quantity.
        for product in invoice_products:   
            current_product = Products.objects.get(pk = product.products.id)
            old_product_quantity = current_product.quantity - product.quantity
            current_product.quantity = old_product_quantity
            #change product status
            if old_product_quantity > 0 :
                current_product.status = 'in-stock'
            else:
                current_product.status = 'out-of-stock'
            
            current_product.save() 
            #update_product_quantity_before_delete(product).save()
            product.delete()
            
        # delete the invoice and the products.
        purchase_instance.delete()
        messages.success(request, 'Purchase deleted successfully')
    
        return redirect('purchase')
    
    messages.warning(request, 'Note: This action can not be undone. ARE YOU SURE YOU WANT TO CONTINUE ?')
    context={
        "title": "Delete: "+purchase_no,
        'invoice_meta': purchase_instance,
        'subtotal': purchase_instance.invoice_amount,
        'details': invoice_products
    }
    return render(request, 'purchase/delete.html',context)

@login_required
def print_purchase(request, purchase_no):
    purchase = Invoice.objects.get(invoice_no = purchase_no)
   
    details = InvoiceActivities.objects.select_related('products').filter(invoice_no_id=purchase.pk).annotate(amount=F("price")*F('quantity'))
    
    context={
        'invoice_meta': purchase,
        'subtotal': purchase.invoice_amount,
        'details': details,
        "title": purchase.invoice_no,
    }
    
    return render(request, "purchase/print.html", context)
   

@login_required
def reports(request):
    return render(request,'reports/index.html')

@login_required
def payments(request):
    return render(request,'payments/index.html')

def current_url_name(request):
    next = request.META.get('HTTP_REFERER', None) or '/'
    return resolve(urlparse(next)[2]).url_name
    
def product_revenue_activity(product_id,invoice_type='sales',price=0):
    invoice = Invoice.objects.filter(invoice_type=invoice_type)
    
    sum_of_quantity = 0
    sum_of_prices = 0
    sum_of_amount = 0
    for each_invoice in invoice:
        
        products = InvoiceActivities.objects.filter(Q(invoice_no_id=each_invoice.id) & Q(products_id = product_id)).aggregate(each_amount= Sum(F("price")*F("quantity")),sum_of_quantity= Sum("quantity"),sum_of_prices= Sum("price"))
       
        
        
        if products['each_amount'] is not None:
            sum_of_quantity = sum_of_quantity + products["sum_of_quantity"]
            sum_of_prices = sum_of_prices + products['sum_of_prices']
            sum_of_amount = sum_of_amount + products["each_amount"]
            
    if sum_of_quantity != 0:
        average_price = float(sum_of_prices/sum_of_quantity)
    else:
        average_price = price
    context = {
        "total_amount": Decimal(sum_of_amount),
        "average_price": Decimal(average_price), 
        "total_quantity_invoiced": sum_of_quantity
    }
    return context
   

def get_product_details(product_code):
    try:
        return Products.objects.get(product_code=product_code)
    except Products.DoesNotExist:
        raise Http404("Record not found or Doesn't exist in the server.")


def get_invoice_details_by_id(invoice_id):
    try:
        return Invoice.objects.get(pk=invoice_id)
    except Products.DoesNotExist:
        raise Http404("Record not found or Doesn't exist in the server.")


def generate_product_code():
    curr_dt = datetime.now()
    return 'PRO'+str(int(round(curr_dt.timestamp())))


def product_progress(qty_in_stock=0,reorder_point=1):
    expected_qty = int(reorder_point) * 5
    percentage = float((qty_in_stock * 100)/expected_qty)
    if percentage >= 100:
        progress_text = 'bg-success'
    elif percentage >= 70:
        progress_text = 'bg-primary'
    elif percentage >= 50:
        progress_text = 'bg-info'
    elif percentage >= 30:
        progress_text = 'bg-warning'
    elif percentage >= 0:
        progress_text = 'bg-danger'
    else:
        progress_text = 'bg-secondary'

    context = {
        'percentage': percentage,
        "progress_text": progress_text,
    }
    return context

#######################AJAX CALLS########################################
@login_required
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def getAjaxProductDetails(request):
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":
        #get the product id
        product_id = request.POST.get('product', None)
        context = {}
        if product_id != '':
            details = Products.objects.get(pk=product_id)
            if current_url_name(request) == 'create_invoice':
                context['price'] = details.selling_price
            elif current_url_name(request) == 'create_purchase':
                context['price'] = details.cost_price
            context['found'] = True
        else:
            context['price'] = 0
            context['found'] = False
        return JsonResponse(context, status=200)
    else:
        pass
    
    # send to client side.
    return render(request, "errors/404.html")

@login_required
def getAjaxPeopleDetails(request):
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":
        #get the people id
        people_id = request.POST.get('people',None)
        if people_id != '':
            if details := People.objects.get(pk=people_id):
                context ={
                    'address': details.address,
                    "phone": details.phone,
                    "email": details.email,
                    'found': True,
                }
                # send to client side.
                return JsonResponse(context, status=200)
            else:
                context['found'] = False
                context["error"] = "Customer does not exist."
                return JsonResponse( context, status=404)
        else: 
            context ={
                'address': "&nbsp;",
                "phone": "&nbsp;",
                "email": "&nbsp;",
                'found': False,
            }
            # send to client side.
            return JsonResponse(context, status=200)
    
    # some error occured
    return render(request, 'errors/404.html')

def createAjaxInvoice(request):
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":
        #get the people id
        
        person_id = int(request.POST.get('people'))
        subtotal = request.POST.get('subtotal', None)
        products = request.POST.get('products', None)
        total_quantity = request.POST.get('total_quantity', None)
        
        context = { 
                   "print":False,
                   "error" : False,
        }
        people_instance = People.objects.filter(pk = person_id, status = 'active')
        people_type = people_instance.first().people_type
        print(people_type)
        if not people_instance.exists():
            context['error'] = True
            context['message'] = 'The customer/vendor does not exit. Please choose another customer/vendor.'
            return JsonResponse(context, status=200)
        
        #save the invoice to generate the id
        data ={
            'total_quantity' : total_quantity,
            'invoice_amount': subtotal,
            'people' : People.objects.get(pk = person_id),
            'invoice_type' : 'sales',
        }
        if people_type == 'vendor':
            data['invoice_type'] = 'purchase'
        
        new_invoice_instance = Invoice.objects.create(**data)
        
        #convert string from ajax to a list of dictionary
        context['person1'] = products
        
        if int(request.POST.get('items', None)) > 1:
            products_ = list(eval(products))
        else:
            #for single item
            products_ = []
            products_.append(json.loads(products))
        
        for product in products_:
            
            data = {
                'invoice_no': new_invoice_instance,
                'products': Products.objects.get(pk=product['product']),
                'quantity': product['quantity'],
                'price':product['price']
            }
            
            InvoiceActivities.objects.create(**data)
            
            #update product quantity
            db_product = Products.objects.get(pk = product['product'])
            
            if people_type == 'customer':
                cal_quantity = float(db_product.quantity) - float(data['quantity'])
                invoice_type = 'invoice'
            elif people_type == 'vendor':
                cal_quantity = float(db_product.quantity) + float(data['quantity'])
                invoice_type = 'purchase'
                
            if cal_quantity <= 0 and db_product.status != 'disabled':
                db_product.status = 'out-of-stock'
            elif cal_quantity >= 0 and db_product.status != 'disabled':
                db_product.status = 'in-stock'
                
            db_product.quantity = cal_quantity
            db_product.save()
        
        #update customer balance
        person = People.objects.get(pk = person_id, status = 'active')
        person.balance = float(person.balance) + float(subtotal)
        person.save()
        
        messages.success(request,'Invoice created successfully.')
        if request.POST.get('action', None) == 'save_print_invoice':
            context['print'] = True
            context['invoice_no'] = reverse('print_invoice',args=(new_invoice_instance.invoice_no,))
        else:
            context['redirect'] = invoice_type
            
        return JsonResponse(context, status=200)
    # some error occured
    return render(request, 'errors/404.html')


        
####################END OF AJAX FUNCTIONS#######################
        
        
        