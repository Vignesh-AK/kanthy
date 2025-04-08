from django.contrib import admin
from .models import Product, Category, Brand, Cart, CartProduct, Order, ProductVariant, ProductImage, Address
# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)
admin.site.register(Address)