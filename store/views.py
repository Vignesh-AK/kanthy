from django.shortcuts import render, get_object_or_404
from .models import Product
from .utils import create_shiprocket_order
import uuid
from .models import Order, Address
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import Cart, CartProduct  # Assuming you have a CartItem model


def product_list(request):
    products = Product.objects.all()
    # Get filter parameters from request
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    colors = request.GET.getlist('color')
    sizes = request.GET.getlist('size')

    # Apply filters
    if min_price.isdigit() and max_price.isdigit():
        products = products.filter(variants__price__gte=min_price, variants__price__lte=max_price).distinct()

    if colors:
        products = products.filter(variants__color__in=colors).distinct()

    if sizes:
        products = products.filter(variants__size__in=sizes).distinct()

    context = {
        'products': products,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
        'selected_colors': colors,
        'selected_sizes': sizes,
    }

    return render(request, 'index.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product-detail.html', {'product': product})

def cart(request):
    if request.user.is_authenticated:
        return render(request, 'cart.html', {"products": request.user})
    else:
        return render(request, 'cart.html')
    
def checkout(request):
    cart_items = Cart.objects.get(user=request.user).cartproduct_set.all()

    total_price = float(sum(item.product.price * item.quantity for item in cart_items))
    tax_amount = total_price * 0.1
    final_total = total_price + tax_amount
    address = request.user.address.all()
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "tax_amount": tax_amount,
        "final_total": final_total,
        "addresses": address,
        "email": request.user.email,
        "phone": request.user.phone,
        "current_address": request.user.address.filter(is_default=True).first()
    }
    return render(request, "checkout.html", context)
    
def save_cart(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                cart_items = data.get("cart", [])

                # Clear existing cart items for the user (optional)
                Cart.objects.filter(user=request.user).delete()

                # Save each item to the database
                cart = Cart.objects.create(user=request.user)
                for item in cart_items:
                    product = Product.objects.get(id=item["id"])  # Check if product exists
                    CartProduct.objects.create(
                        cart=cart,
                        product=product,
                        quantity=item.get("quantity", 1)  # Default to 1 if not provided
                    )

                return JsonResponse({"success": True})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
        else:
            return JsonResponse({"success": False, "error": "User not authenticated", }, status=401)
    return JsonResponse({"success": False, "error": "Invalid request"})
    


def place_order(request):
    # if request.method == "POST":
        # Extract form data (customize based on your frontend form)
    customer_name = "Vignesh"
    customer_email = "vigneshayanikodan@gmail.com"
    customer_phone = "917561071623"
    address = Address.objects.get(user=request.user, is_default=True)
    city = "Chennai"
    pincode = "600001"
    state = "Tamil Nadu"
    total_amount =  1000  # Total amount of the order

    # Create order in your database
    order = Order.objects.create(
        order_id=str(uuid.uuid4()),  # Unique order ID
        quantity=1,
        user=request.user,
        address=address,
        # city=city,
        # pincode=pincode,
        # state=state,
        total_price=total_amount
    )
    
    # Send order to Shiprocket
    try:
        shiprocket_response = create_shiprocket_order(order)
        order.status = "Shiprocket Created"
        order.save()
        return render(request, "order_success.html", {"order": order, "shiprocket": shiprocket_response})
    except Exception as e:
        return render(request, "order_error.html", {"error": str(e)})
    
def privacy_policy(request):
    return render(request, 'privacy_policy.html')