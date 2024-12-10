from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('create-order/', views.create_order, name='create_order'),
    path('paypal/', include("paypal.standard.ipn.urls")),  # Подключение URL-ов для PayPal IPN
    path('paypal/success/<int:order_id>/', views.paypal_success, name='paypal_success'),
    path('paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),
]
