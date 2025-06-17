from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from store.models import Address, CartProduct
from django.http import JsonResponse



def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        auth = authenticate(username=username, password=password)
        if auth is not None:
            login(request, auth)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:   
        return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
    else:
        return render(request, 'register.html')
    
def add_address(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')

        Address.objects.create(
            user=request.user,
            address=address,
            city=city,
            state=state,
            country="India",
            pincode=zip_code,
            is_default=True
        )

        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

def profile(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html', {
            'user': request.user,
            'orders': request.user.order_set.all(),
            'addresses': Address.objects.filter(user=request.user),
            "cart_quantity": sum(item.quantity for item in CartProduct.objects.filter(cart__user=request.user)) if request.user.is_authenticated else 0
        })
    else:
        return redirect('login')