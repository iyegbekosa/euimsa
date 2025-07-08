from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('history/', views.history_view, name='history'),
    path('account/', views.account_view, name='account'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('get-amount/', views.get_amount, name='get_amount'),
    path('split/', views.initialize_split_payment, name='split'),
    path('payment/verify/', views.paystack_callback, name='paystack_callback'),
    path('payment/receipt/<str:ref>/', views.payment_receipt, name='payment_receipt'),
]
