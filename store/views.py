from django.shortcuts import render, get_object_or_404

from payment.models import Payment
from .models import Product
from .utils import create_shiprocket_order
import uuid
from .models import Order, Address
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import Cart, CartProduct  # Assuming you have a CartItem model
import razorpay
from django.conf import settings

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
    

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def place_order(request):
    # if request.method == "POST":
        # Extract form data (customize based on your frontend form)
    # customer_name = request.user.first_name + " " + request.user.last_name
    # customer_email = request.user.email
    # customer_phone = request.user.phone
    data = json.loads(request.body.decode("utf-8"))
    print("Data received:", data)
    address = Address.objects.get(user=request.user, is_default=True)
    # city = address.city
    # pincode = address.pincode
    # state = address.state
    amount = data.get("price")  # Total amount of the order

    print("Amount:", amount)
    quantity = request.POST.get("quantity", 1)  # Default to 1 if not provided
    # Create order in your database
    order = Order.objects.create(
        order_id=str(uuid.uuid4()),  # Unique order ID
        quantity=quantity,
        user=request.user,
        address=address,
        total_price=float(amount)
    )
    
    currency = 'INR'

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=float(amount),
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'https://kanthy.com/payment/payment-handler/'

    # we need to pass these details to frontend.
    # context = {}
    # context['razorpay_order_id'] = razorpay_order_id
    # context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    # context['razorpay_amount'] = amount
    # context['currency'] = currency
    # context['callback_url'] = callback_url
    Payment.objects.create(
        order=order,
        user=request.user,
        amount=amount,
        status='pending',
        transaction_id=razorpay_order_id,
    )
    print("Payment created:", float(amount)*100)
    return JsonResponse({
        'success': True,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'amount': float(amount)*100,  # Convert to paise
        'currency': currency,
        'callback_url': callback_url
    })

    # Send order to Shiprocket
    
    
def privacy_policy(request):
    return render(request, 'privacy_policy.html')