from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('products/<slug:product_type>/', views.product_list_filter, name='product_list_filter'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('save-cart/', views.save_cart, name='save_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('remove-cart/', views.remove_cart, name='remove-cart'),
    path('test/', views.test, name='test'),
    path('update-quantity/', views.update_quantity, name="update-quantity"),
    path('add-to-cart/', views.add_to_cart, name="add-to-cart")
]