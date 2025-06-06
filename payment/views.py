from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse

from payment.models import Payment
from store.utils import create_shiprocket_order


# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@csrf_exempt
def homepage(request):
    currency = 'INR'
    amount = 20000  # Rs. 200

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'https://kanthy.com/payment/payment-handler/'

    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request, 'payment.html', context=context)


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
    print("Payment Handler Called")
    # only accept POST request.
    if request.method == "POST":
        # try:
          
            # get the required parameters from post request.
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        print("Payment ID: ", payment_id)
        print("Razorpay Order ID: ", razorpay_order_id)
        print("Signature: ", signature)
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        # verify the payment signature.
        result = razorpay_client.utility.verify_payment_signature(
            params_dict)
        if result is not None:
            print("Signature Verified")
            payment = Payment.objects.get(transaction_id=razorpay_order_id)
            order = payment.order
            payment.payment_id = payment_id
            payment.status = "completed"
            amount = float(payment.amount)
            # try:
                # capture the payemt
            razorpay_client.payment.capture(payment_id, amount)
            try:
                shiprocket_response = create_shiprocket_order(order)
                order.status = "Shiprocket Created"

                order.save()
                return render(request, "order_success.html", {"order": order, "shiprocket": shiprocket_response})
            except Exception as e:
                return render(request, "order_error.html", {"error": str(e)})
            # render success page on successful caputre of payment
            # return render(request, 'paymentsuccess.html')
            # except:

                # if there is an error while capturing payment.
                # return render(request, 'paymentfail.html')
        else:

            # if signature verification fails.
            return render(request, 'paymentfail.html')
        # except:

        #     # if we don't find the required parameters in POST data
        #     return render(request, 'paymentfail.html')
    else:
       # if other than POST request is made.
        print("Payment Handler Called not post")
        return render(request, 'paymentfail.html')


@csrf_exempt
def test_view(request):
    print("Payment Handler Called")
    return JsonResponse({"ok": True})