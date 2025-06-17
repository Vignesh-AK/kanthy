from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('add-address/', views.add_address, name='add-address'),
    path('profile/', views.profile, name='profile'),
    
]