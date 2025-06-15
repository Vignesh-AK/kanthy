from django.contrib import admin
from .models import Product, Category, Brand, Cart, CartProduct, Order, ProductVariant, ProductImage, Address, ProductColor
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
admin.site.register(ProductColor)

admin.site.site_header = "Kanthy Admin"
admin.site.site_title = "Kanthy Admin Portal"
admin.site.index_title = "Welcome to Kanthy Admin Portal"

# This admin.py file registers the models for the Kanthy application with the Django admin site.
# It allows the admin interface to manage products, categories, brands, carts, orders, and addresses.
# The admin interface provides a user-friendly way to create, read, update, and delete these models.
# The admin site is customized with a header, title, and index title to reflect the Kanthy brand.
# The models registered include:
# - Product: Represents products available in the store.
# - Category: Represents product categories for better organization.
# - Brand: Represents brands associated with products.
# - Cart: Represents a user's shopping cart.                