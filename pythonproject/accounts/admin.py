from django.contrib import admin
from .models import Accounts, Account_activities

# Register your models here.
admin.site.register(Accounts)
admin.site.register(Account_activities)