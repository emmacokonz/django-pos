from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from operator import attrgetter
from itertools import chain
import calendar
from decimal import Decimal
from os import name
from turtle import st
from urllib.parse import urlparse
from django.contrib import messages
from django.http import Http404
from django.urls import reverse, resolve
from django.views.generic.base import View
from django.db.models import Sum, F, Q, Avg
from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Accounts, Account_activities
from productmgt.models import People, Invoice, Products, InvoiceActivities
from django.contrib.auth.models import User

DATE_RANGE_SETTINGS = 'this month'
PREVIOUS_DATE_RANGE_SETTINGS = DATE_RANGE_SETTINGS.replace('this', 'last')
SALES = 'sales'
CUSTOMERS = 'customer'
OUT_OF_STOCK = "out-of-stock"

@login_required
def index(request):
    context = {
        'title': 'Dashboard',
        'filter': DATE_RANGE_SETTINGS,
        'total_sales': get_total_sales()['count'],
        'cash_inflows': get_cash_inflow()["cash_inflow"],
        'customers': get_total_customers()['count'],
        'products': get_out_of_stock()['count'],
        'top_stocks': get_top_stocks(),
        'latest_transactions': get_latest_transactions(),
        'payables': calculate_payables(),
        'receiveables': calculate_receiveables(),
        'cash': calculate_cash(),
        'customers_revenue': get_customers_revenue(),
    }
    return render(request, 'dashboard.html', context)

def get_customers_revenue():
    customers_revenue = People.objects.filter(people_type = "customer").annotate(
        customer_invoice_amount_sum = Sum('invoice__invoice_amount', default=0, filter=Q(invoice__created_at__range=(get_settings_date_range()[0],get_settings_date_range()[1])))).values(
        'name','customer_invoice_amount_sum').order_by(
        "-customer_invoice_amount_sum")[:5]
    total_revenue = People.objects.filter(people_type = 'customer').aggregate(
        total_invoice_amount = Sum('invoice__invoice_amount', default=0, filter=Q(invoice__created_at__range=(get_settings_date_range()[0],get_settings_date_range()[1]))))

    for cr in customers_revenue :
        if float(total_revenue['total_invoice_amount']) != 0:
            p = float(cr['customer_invoice_amount_sum']) * 100/float(total_revenue['total_invoice_amount'])
        else:
            p=0
        cr['percentage'] = p


    return customers_revenue


def calculate_cash():
    cash = Accounts.objects.filter(account_type = 'bank').aggregate(sum_total = Sum('account_balance'))
    return cash

def calculate_payables():
    people_instance = People.objects.filter(Q(people_type='vendor') & Q(status='active')).aggregate(sum_total = Sum('balance'))

    return people_instance


def calculate_receiveables():
    people_instance = People.objects.filter(Q(people_type='customer') & Q(status='active')).aggregate(sum_total = Sum('balance'))

    return people_instance


def get_latest_transactions():
    payments = Account_activities.objects.filter(Q(payment_type='sales') | Q(payment_type = 'bill')).order_by("-id")
    invoices = Invoice.objects.all().order_by("-id")
    result_list =  sorted(chain(payments,invoices),reverse=True,key=attrgetter('created_at'))[:10]

    return result_list

def get_top_stocks():

    most_sold_products = Products.objects.filter(
        invoiceactivities__invoice_no__invoice_type = SALES).annotate(
        current_stock_out_sum = Sum('invoiceactivities__quantity', default=0, filter=Q(invoiceactivities__invoice_no__created_at__range=(get_settings_date_range()[0],get_settings_date_range()[1])))).annotate(
        previous_stock_out_sum = Sum('invoiceactivities__quantity', default=0, filter=Q(invoiceactivities__invoice_no__created_at__range=(get_previous_settings_date_range()[0],get_previous_settings_date_range()[1])))).values_list(
        'name','current_stock_out_sum',"status", 'quantity','previous_stock_out_sum', named=True).order_by(
        "-current_stock_out_sum")[:5]

    return most_sold_products

def get_out_of_stock():

    products = Products.objects.filter(status = OUT_OF_STOCK)
    context={
        'count' : len(products),
        'products': products
    }
    return context

def get_total_customers():

    customers = People.objects.filter(people_type = CUSTOMERS)
    context={
        'count' : len(customers),
        'customers': customers
    }
    return context

def get_cash_inflow():

    cash = Account_activities.objects.filter(payment_type=SALES,created_at__range=(get_settings_date_range()[0],get_settings_date_range()[1])).aggregate(cash_inflow = Sum('amount', default=0))
    return cash

def get_total_sales():
    count = Invoice.objects.filter(created_at__range=(get_settings_date_range()[0],get_settings_date_range()[1]), invoice_type = SALES)
    context={
        'count' : len(count),
        'sales': count
    }
    return context

def get_previous_settings_date_range():

    current_timezone = timezone.get_current_timezone()
    today_date = datetime.now(tz = current_timezone)

    if PREVIOUS_DATE_RANGE_SETTINGS == 'last month':
        #set the date to the last day of last month
        previous_month = today_date + relativedelta(months=-1, day=31)

        from_date = datetime(year=previous_month.year, month=previous_month.month, day=1,tzinfo= current_timezone)
        to_date = datetime(year=previous_month.year, month=previous_month.month, day=previous_month.day,tzinfo= current_timezone)

    return (from_date, to_date)

def get_settings_date_range():

    current_timezone = timezone.get_current_timezone()
    today_date = datetime.now(tz = current_timezone)

    if DATE_RANGE_SETTINGS == 'this month':
        from_date = datetime(year=today_date.year, month=today_date.month, day=1,tzinfo= current_timezone)
        to_date = datetime.now(tz = current_timezone)

    elif DATE_RANGE_SETTINGS == 'last 7 days':
        from_date = today_date - timedelta(days=7)
        to_date = datetime.now(tz = current_timezone)
    elif DATE_RANGE_SETTINGS == 'today':
        from_date = today_date
        to_date = datetime.now(tz = current_timezone)
    else:
        from_date = date(year=today_date.year, month=1, day=1)
        to_date = datetime.now(tz = current_timezone)

    return (from_date, to_date)
