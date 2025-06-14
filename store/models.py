from django.db import models
from users.models import CustomUser
from django.utils import timezone
import uuid

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=30)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    product_type = models.CharField(max_length=50, choices=[
        ('new_arrival', 'New Arrival'),
        ('best_seller', 'Best Seller'),
        ('casual_wear', 'Casual Wear'),
        ('wedding_wear', 'Wedding Wear'),
        ('sarees', 'Sarees'),
        ('kurtas', 'Kurtas'),
    ], default='new_arrival')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_discounted = models.BooleanField(default=False)

    
    def __str__(self):
        return self.name

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors")
    color = models.CharField(max_length=50)
    image = models.ImageField(upload_to="product_color_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.color}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    product_color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name="variants", null=True, blank=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.product_color.color if self.product_color else 'No Color'}"


class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_images/")

    def __str__(self):
        return f"Image for {self.variant.product.name} - {self.variant.size} - {self.variant.product_color.color if self.variant.product_color else 'No Color'}"


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cart.user.username} - {self.product.name} ({self.quantity})"

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='address')
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.address} - {self.city}, {self.state}, {self.country} - {self.pincode}"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"
    
class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    delivery_date = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=12, choices=STATUS_CHOICES)


class Invoice(models.Model):
    invoice_id = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='order')
