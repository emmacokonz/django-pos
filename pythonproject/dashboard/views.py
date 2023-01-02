from datetime import datetime, date, timedelta
import calendar
from decimal import Decimal
from os import name
from turtle import st
from urllib.parse import urlparse
from django.contrib import messages
from django.http import Http404
from django.urls import reverse, resolve
from django.views.generic.base import View
from django.db.models import Sum, F, Q
from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Accounts, Account_activities
from productmgt.models import People, Invoice
from django.contrib.auth.models import User

DATE_RANGE_SETTINGS = 'this month'

def index(request):
    get_total_sales()
    return render(request, 'dashboard.html')

def get_total_sales():
    get_settings_date_range()
    count = Invoice.objects.filter(created_at__range=(get_settings_date_range()[0],get_settings_date_range()[1])) 
    
    print(count)
    

def get_settings_date_range():
    today_date = date.today()
    if DATE_RANGE_SETTINGS == 'this month':
        from_date = date(year=today_date.year, month=today_date.month, day=1)
        to_date = datetime.today() #+ timedelta(days=7)
        
    elif DATE_RANGE_SETTINGS == 'last 7 days':
        from_date = today_date - timedelta(days=7)
        to_date = datetime.today()
    elif DATE_RANGE_SETTINGS == 'today':
        from_date = today_date
        to_date = datetime.today()
    else:
        from_date = date(year=today_date.year, month=1, day=1)
        to_date = datetime.today() 
        
    return (from_date, to_date)
    