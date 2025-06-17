from django.shortcuts import render, get_object_or_404

from payment.models import Payment
from .models import Product
from .utils import create_shiprocket_order, get_estimated_delivery_date, get_shiprocket_token
import uuid
from .models import Order, Address, OrderItem
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
        # products = products.filter(variants__color__in=colors).distinct()
        products = products.filter(variants__product_color__color__in=colors).distinct()

    if sizes:
        products = products.filter(variants__size__in=sizes).distinct()

    context = {
        'products': products,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
        'selected_colors': colors,
        'selected_sizes': sizes,
        'cart_quantity': sum(item.quantity for item in CartProduct.objects.filter(cart__user=request.user)) if request.user.is_authenticated else 0,
    }
    print("Context:", context)
    return render(request, 'index.html', context)

def product_list_filter(request, product_type):
    products = Product.objects.filter(product_type=product_type)
    # Get filter parameters from request
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    colors = request.GET.getlist('color')
    sizes = request.GET.getlist('size')

    # Apply filters
    if min_price.isdigit() and max_price.isdigit():
        products = products.filter(variants__price__gte=min_price, variants__price__lte=max_price).distinct()

    if colors:
        # products = products.filter(variants__color__in=colors).distinct()
        products = products.filter(variants__product_color__color__in=colors).distinct()

    if sizes:
        products = products.filter(variants__size__in=sizes).distinct()

    context = {
        'products': products,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
        'selected_colors': colors,
        'selected_sizes': sizes,
        'cart_items': CartProduct.objects.filter(cart__user=request.user) if request.user.is_authenticated else [],
        'cart_quantity': sum(item.quantity for item in CartProduct.objects.filter(cart__user=request.user)) if request.user.is_authenticated else 0,
    }

    return render(request, 'index.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_quantity = sum(item.quantity for item in CartProduct.objects.filter(cart__user=request.user)) if request.user.is_authenticated else 0
    cart_items = CartProduct.objects.filter(cart__user=request.user) if request.user.is_authenticated else []

    return render(request, 'product-detail.html', {'product': product, 'cart_quantity': cart_quantity})

def cart(request):
    if request.user.is_authenticated:
        products = CartProduct.objects.filter(cart__user=request.user)
        products_list = []
        total = 0
        delivery = 40
        discount = 100
        for product in products:
        #    for count in range(product.quantity):
            products_list.append({ 
            "image" : product.product.image.url if product.product.image else None,
            "name" : product.product.name,
            "price" : float(product.product.price),
            "id": product.id,
            "quantity": product.quantity,
            })
            total += (float(product.quantity)*float(product.product.price))
        cart = {
            "total": total+delivery-discount,
            "products": products_list,
            "discount": discount,
            "amount": total,
            "delivery_charge": delivery
        }
        print(cart)
        cart_quantity = sum(item.quantity for item in CartProduct.objects.filter(cart__user=request.user)) if request.user.is_authenticated else 0
        return render(request, 'cart.html', {"cart": json.dumps(cart), "price": cart,"user": request.user, 'cart_quantity': cart_quantity})
    else:
        return render(request, 'cart.html')
    
def checkout(request):
    cart_items = Cart.objects.get(user=request.user).cartproduct_set.all()

    total_price = float(sum(item.product.price * item.quantity for item in cart_items))
    delivery = 40
    discount = 100
    tax_amount = total_price * 0.1
    final_total = total_price + tax_amount + delivery - discount
    address = request.user.address.all()
    context = {
        "cart_items": cart_items,
        "total_price": total_price ,
        "discount": discount,
        "delivery": delivery,
        "tax_amount": tax_amount,
        "final_total": final_total,
        "email": request.user.email,
        "phone": request.user.phone,
        "current_address": address.filter(is_default=True).first(),
        "addresses": address,
        "cart_quantity": sum(item.quantity for item in CartProduct.objects.filter(cart__user=request.user)) if request.user.is_authenticated else 0
    }
    return render(request, "checkout.html", context)
    
def save_cart(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            # try:
            data = json.loads(request.body)
            cart_items = data.get("cart", [])

            # Clear existing cart items for the user (optional)
            # Cart.objects.filter(user=request.user).delete()

            # Save each item to the database
            is_cart = Cart.objects.filter(user=request.user).exists()
            if is_cart:
                print("cart is there")
                cart = Cart.objects.get(user=request.user)
                for item in cart_items:
                    print(item)
                    product = Product.objects.get(id=item["id"])  # Check if product exists
                    if CartProduct.objects.filter(cart=cart, product=product).exists():
                        cart_product = CartProduct.objects.get(cart=cart, product=product)
                        cart_product.quantity += item.get("quantity", 1)
                        cart_product.save()
                    else:
                        CartProduct.objects.create(
                            cart=cart,
                            product=product,
                            quantity=item.get("quantity", 1)  # Default to 1 if not provided
                        )
                        print("else working ")
                    
            else:
                cart = Cart.objects.create(user=request.user)
                for item in cart_items:
                    product = Product.objects.get(id=item["id"])
                    CartProduct.objects.create(
                        cart=cart,
                        product=product,
                        quantity=item.get("quantity", 1)  # Default to 1 if not provided
                    )
            return JsonResponse({"success": True})
            # except Exception as e:
            #     return JsonResponse({"success": False, "error": str(e)})
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
    address_id = data.get('address')
    address = Address.objects.get(id=address_id)
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
    for product in CartProduct.objects.filter(cart__user=request.user):
        OrderItem.objects.create(
            product=product.product,
            quantity= product.quantity,
            order = order
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

def remove_cart(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                product_id = data.get("index")
                print(product_id)

                # Get the user's cart
                # Find the cart product and delete it
                cart_product = CartProduct.objects.get(id=int(product_id))
                cart_product.delete()

                return JsonResponse({"success": True, "message": "Product removed from cart"})
            except CartProduct.DoesNotExist:
                return JsonResponse({"success": False, "error": "Product not found in cart"})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
        else:
            return JsonResponse({"success": False, "error": "User not authenticated"}, status=401)
    return JsonResponse({"success": False, "error": "Invalid request"})

def update_quantity(request):
    data = json.loads(request.body)
    product_id = data.get("id")
    action = data.get("action")
    
    product = CartProduct.objects.get(id=int(product_id))
    if action == "increase":
        product.quantity += 1
    else:
        product.quantity -= 1
    product.save()
    return JsonResponse({"success": True, "message": "Updated"})

def test(request):
    token = get_shiprocket_token()
    pickup_pincode = "679332"
    delivery_pincode = "679332"
    get_estimated_delivery_date(token, pickup_pincode, delivery_pincode, weight=1, cod=0)

def add_to_cart(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    # try:
    data = json.loads(request.body)

    product_id = data.get("id")
    quantity = 1  # Default quantity is 1
    user = request.user
    # Fetch the product
    product = Product.objects.get(pk=product_id)
    if Cart.objects.filter(user=user).exists():
    # Check if item already exists in user's cart
        cart = Cart.objects.get(user=user)
        if CartProduct.objects.filter(cart=cart, product=product).exists():
            cart_product = CartProduct.objects.get(cart=cart, product=product)
            cart_product.quantity += 1
            cart_product.save()
        else:
            CartProduct.objects.create(
            cart=cart,
            product=product, quantity=quantity)
            

    return JsonResponse({"success": True, "message": "Item added to cart."})

    # except Product.DoesNotExist:
    #     return JsonResponse({"success": False, "message": "Product not found."}, status=404)

    # except Exception as e:
    #     return JsonResponse({"success": False, "message": str(e)}, status=500)

