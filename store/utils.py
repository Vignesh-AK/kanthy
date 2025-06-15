import requests
import json

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
    order_items = [
        {
            "name": "T-Shirt",  # Replace with dynamic item name
            "sku": "TSHIRT001",
            "units": 1,
            "selling_price": str(order.total_price),
            "discount": 0,
            "tax": 0,
            "hsn": "6109"  # HSN code for clothing
        }
    ]
    
    payload =  {
  "order_id": "ORD123456",
  "order_date": "2025-06-06",
  "pickup_location": "Home",
  "channel_id": "",
  "comment": "Handle with care",
  "reseller_name": "John Doe Reseller",
  "company_name": "Wonderstroke Arts Pvt Ltd",
  "billing_customer_name": "John",
  "billing_last_name": "Doe",
  "billing_address": "123, MG Road",
  "billing_address_2": "Near Central Mall",
  "billing_isd_code": "+91",
  "billing_city": "Bangalore",
  "billing_pincode": "560001",
  "billing_state": "Karnataka",
  "billing_country": "India",
  "billing_email": "john.doe@example.com",
  "billing_phone": "7561071623",
  "billing_alternate_phone": "7561071623",
  "shipping_is_billing": True,
  "shipping_customer_name": "John",
  "shipping_last_name": "Doe",
  "shipping_address": "123, MG Road",
  "shipping_address_2": "Near Central Mall",
  "shipping_city": "Bangalore",
  "shipping_pincode": "560001",
  "shipping_country": "India",
  "shipping_state": "Karnataka",
  "shipping_email": "john.doe@example.com",
  "shipping_phone": "7561071623",
  "order_items": [
    {
      "name": "Canvas Painting - Sunset",
      "sku": "PAINT-SUNSET-001",
      "units": 1,
      "selling_price": "2999",
      "discount": "200",
      "tax": "18",
      "hsn": "9701"
    },
    {
      "name": "Sketch Portrait",
      "sku": "SKETCH-JOHN-001",
      "units": 1,
      "selling_price": "1499",
      "discount": "100",
      "tax": "18",
      "hsn": "9701"
    }
  ],
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
  "invoice_number": "INV-56789",
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
