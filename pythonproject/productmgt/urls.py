from django.urls import path,include
from . import views

urlpatterns = [
    path('products/', views.productsList, name='products'),
    path('products/new/', views.new_product, name='new_product'),
    path('products/<str:product_code>', views.productDetails, name='product_details'),
    path('products/edit/<str:product_code>', views.edit_product, name='edit_product'),
    path('products/delete/<str:product_code>', views.delete_product, name='delete_product'),
    path('products/disable/<str:product_code>', views.disable_product, name='disable_product'),
    path('products/enable/<str:product_code>', views.enable_product, name='enable_product'),
    path('products/ajax/get_a_product/', views.getAjaxProductDetails, name="get_a_product_ajax"),
    
    
    path('invoice/', views.invoice, name='invoice'),
    path('invoice/new', views.create_invoice, name="create_invoice"),
    path('invoice/<str:invoice_no>',views.invoiceDetails, name="view_invoice"),
    path('invoice/edit/<str:invoice_no>',views.edit_invoice, name="edit_invoice"),
    path('invoice/print/<str:invoice_no>', views.print_invoice, name='print_invoice'),
    path('invoice/delete/<str:invoice_no>', views.delete_invoice, name='delete_invoice'),
    path('products/ajax/create_invoice/', views.createAjaxInvoice, name="create_new_invoice_ajax"),
    
    path('purchase/', views.purchase, name='purchase'),
    path('purchase/new', views.create_purchase, name="create_purchase"),
    path('purchase/<str:purchase_no>',views.purchaseDetails, name="view_purchase"),
    path('purchase/edit/<str:invoice_no>',views.edit_purchase, name="edit_purchase"),
    path('purchase/print/<str:purchase_no>', views.print_purchase, name='print_purchase'),
    path('purchase/delete/<str:purchase_no>', views.delete_purchase, name='delete_purchase'),
    
    
    path('people/', views.people, name='people'),
    path('people/new/', views.new_people, name='new_people'),
    path('people/<int:people_id>', views.peopleDetails, name='people_details'),
    path('people/edit/<int:people_id>', views.edit_people, name='edit_people'),
#   path('people/delete/<int:people_id>', views.delete_people, name='delete_people'),
    path('people/disable/<int:people_id>', views.disable_people, name='disable_people'),
    path('people/enable/<int:people_id>', views.enable_people, name='enable_people'),
    path('people/ajax/get_a_person/', views.getAjaxPeopleDetails, name="get_a_person_ajax"),
    
]
