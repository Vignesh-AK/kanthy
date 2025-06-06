# dj_razorpay/urls.py

from django.contrib import admin
from django.urls import path
from payment import views

urlpatterns = [
    path('', views.homepage, name='index'),
    path('payment-handler/', views.paymenthandler, name='paymenthandler'),
    path('test/', views.test_view, name='test'),
]
