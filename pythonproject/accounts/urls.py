from django.urls import path, include
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
    path('payments/<int:transaction_id>/', views.get_transaction_details, name='payment'),
    path('payments/edit/<int:payment_id>', views.edit_payment, name='edit_payment'),
    path('make_payment/', views.make_payment, name='make_payment'),
    path('receive_payment/', views.receive_payment, name='receive_payment'),
    path('payments/delete/<int:transaction_id>', views.delete_transaction, name='delete_transaction'),
    path('transfer/', views.make_transfer, name='make_transfer'),
    path('transfer/<int:transaction_id>/', views.get_transaction_details, name='transfer'),
    path('transfer/edit/<int:transfer_id>', views.edit_transfer, name='edit_transfer'),
    path('transfer/delete/<int:transaction_id>', views.delete_transaction, name='delete_transaction'),
    path('expenses/', views.expenses, name='expenses'),
    path('expenses/<int:transaction_id>/', views.get_transaction_details, name='expense'),
    path('expenses/edit/<int:expenses_id>', views.edit_expenses, name='edit_expenses'),
    path('expenses/delete/<int:transaction_id>', views.delete_transaction, name='delete_transaction'),
    path('expenses/new', views.new_expenses, name='new_expenses'),
]
