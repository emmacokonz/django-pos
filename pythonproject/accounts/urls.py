from django.urls import path,include
from . import views

urlpatterns = [
    path('accounts/', views.index, name='accounts'),
    path('accounts/new/', views.new_account, name='new_account'),
    path('accounts/edit/<int:account_id>/', views.edit_account, name='edit_account'),
    path('accounts/delete/<int:account_id>/', views.delete_account, name='delete_account'),
    path('accounts/payables/', views.payables, name='payables'),
    path('accounts/receiveables/', views.receiveables, name='receiveables'),    
    path('accounts/<int:account_id>/', views.get_account, name='get_account'),
    
    path('payments/', views.payments, name='payments'),
    path('payments/<int:payment_id>/', views.payments, name='payment'),
    path('make_payment/', views.make_payment, name='make_payment'),
    path('receive_payment/', views.receive_payment, name='receive_payment'),
    path('transfer/', views.make_transfer, name='transfer'),
]
