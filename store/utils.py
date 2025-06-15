import requests
import json
from store.models import OrderItem
from datetime import datetime

def get_shiprocket_token():
    url = "https://apiv2.shiprocket.in/v1/external/auth/login"
    payload = {
        "email": "vchoo10@gmail.com",  # Replace with your Shiprocket email
        "password": "7456@Kanthy"         # Replace with your Shiprocket password
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        token = response.json().get("token")
        return token
    else:
        raise Exception("Failed to authenticate with Shiprocket")
    

def create_shiprocket_order(order):
    token = get_shiprocket_token()
    url = "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc"
    
    # Sample order items (adjust based on your clothing items)
    # order_items = [
    #     {
    #         "name": "T-Shirt",  # Replace with dynamic item name
    #         "sku": "TSHIRT001",
    #         "units": 1,
    #         "selling_price": str(order.total_price),
    #         "discount": 0,
    #         "tax": 0,
    #         "hsn": "6109"  # HSN code for clothing
    #     }
    # ]
    order_items = []
    for item in OrderItem.objects.filter(order=order):
        order_items.append({
            "name": item.product.name,  # Replace with dynamic item name
            "sku": item.product.id,
            "units": item.quantity,
            "selling_price": item.product.price,
            "discount": 0,
            "tax": 0,
            "hsn": "6109"  # HSN code for clothing
        })
    today = datetime.today()
    formatted_date = today.strftime('%Y-%m-%d')
    payload =  {
  "order_id": order.order_id,
  "order_date": formatted_date,
  "pickup_location": "Home",
  "channel_id": "",
  "comment": "Handle with care",
  "reseller_name": "John Doe Reseller",
  "company_name": "Wonderstroke Arts Pvt Ltd",
  "billing_customer_name": "Binu",
  "billing_last_name": "Pv",
  "billing_address": "A208, ss snowdrops, Belathur Main road",
  "billing_address_2": "Whitefield, Kadugodi",
  "billing_isd_code": "+91",
  "billing_city": "Bangalore",
  "billing_pincode": "560001",
  "billing_state": "Karnataka",
  "billing_country": "India",
  "billing_email": "sales@kanthy.com",
  "billing_phone": "7561071623",
  "billing_alternate_phone": "7561071623",
  "shipping_is_billing": True,
  "shipping_customer_name": order.user.first_name,
  "shipping_last_name": order.user.last_name,
  "shipping_address": order.address.address,
  "shipping_address_2": order.address.address,
  "shipping_city": order.address.city,
  "shipping_pincode": order.address.pincode,
  "shipping_country": order.address.country,
  "shipping_state": order.address.state,
  "shipping_email": order.user.email,
  "shipping_phone": order.user.phone,
  "order_items": order_items,
  "payment_method": "Prepaid",
  "shipping_charges": "100",
  "giftwrap_charges": "50",
  "transaction_charges": "20",
  "total_discount": "300",
  "sub_total": "4398",
  "length": "30",
  "breadth": "20",
  "height": "5",
  "weight": "1.2",
  "ewaybill_no": "",
  "customer_gstin": "",
  "invoice_number": order.invoice.invoice_id,
  "order_type": "ESSENTIALS"
}
    # print("Payload for Shiprocket:", payload)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Order created successfully:", response.json())
        return response.json()
    else:
        print("Failed to create order:", response.text)
        raise Exception(f"Failed to create order: {response.text}")


def get_estimated_delivery_date(token, pickup_pincode, delivery_pincode, weight=1, cod=0):
    url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
    data = {
                "pickup_postcode": "679332",
                "delivery_postcode": "679332",
                "weight": 1,
                "cod": 0,
            }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers, data=json.dumps(data))
    print(response.json())
    return response.json()
