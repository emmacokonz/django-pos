from django.contrib import admin
from .models import InvoiceActivities, Products, People, Invoice

# Register your models here.
admin.site.register(Products)
admin.site.register(People)
admin.site.register(Invoice)
admin.site.register(InvoiceActivities)