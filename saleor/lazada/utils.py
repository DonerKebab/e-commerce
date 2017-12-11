from hashlib import sha256
from hmac import HMAC
from datetime import datetime
import json
from urllib.parse import urlencode
from urllib.parse import quote
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from decimal import Decimal

from ..order.models import DeliveryGroup, Order, OrderedItem
from ..userprofile.models import Address, User

ENDPOINT = {
    'GetOrders': 'GetOrders',
    'GetOrderItems': 'GetOrderItems',
    'SetStatusToPackedByMarketplace': 'SetStatusToPackedByMarketplace',
    'SetStatusToReadyToShip': 'SetStatusToReadyToShip',
    'GetDocument': 'GetDocument',
    'GetOrder': 'GetOrder'
}

ORDER_STATUS = {
    'pending': 'pending',
    'canceled': 'canceled',
    'ready_to_ship': 'ready_to_ship',
    'delivered': 'delivered',
    'returned': 'returned',
    'shipped': 'shipped',
    'failed': 'failed'
}

def get_timestamp():
    timestamp = datetime.now().isoformat()
    timestamp = timestamp[:timestamp.index('.')] + '+07:00'

    return timestamp


def generate_signature(parameters):
    concatenated = urlencode(sorted(parameters.items())).encode('utf-8')
    return HMAC(b'aRsLXa5EzE8ycwEpfxw6xfQJcpfuS3O0FSGi9E_znajmrIh1Ua45x1m0', concatenated, sha256).hexdigest()

def get_orders(status):

    parameters = {
      'Action': ENDPOINT['GetOrders'],
      'Format':'json',
      'Timestamp': get_timestamp(),
      'UserID': settings.LAZADA_USER_ID,
      'Version': '1.0',
      'Status': status,
      'Limit': 500,
      'CreatedAfter': '2014-02-25T23:46:11+00:00'
    }

    parameters['Signature'] = generate_signature(parameters)

    res = requests.get(settings.LAZADA_ENDPOINT_URI, parameters)
    return json.loads(res.text)

def get_orders_by_id(order_id):

    parameters = {
      'Action': ENDPOINT['GetOrder'],
      'Format':'json',
      'Timestamp': get_timestamp(),
      'UserID': settings.LAZADA_USER_ID,
      'Version': '1.0',
      'OrderId': order_id,
      'Limit': 500,
      'CreatedAfter': '2014-02-25T23:46:11+00:00'
    }

    parameters['Signature'] = generate_signature(parameters)

    res = requests.get(settings.LAZADA_ENDPOINT_URI, parameters)
    return json.loads(res.text)


def get_pending_orders():
    pending_orders = get_orders(ORDER_STATUS['pending'])
    return pending_orders['SuccessResponse']['Body']['Orders']

def get_canceled_orders():
    canceled_orders = get_orders(ORDER_STATUS['canceled'])
    return canceled_orders['SuccessResponse']['Body']['Orders']

def get_ready_orders():
    ready_to_ship_orders = get_orders(ORDER_STATUS['ready_to_ship'])
    return ready_to_ship_orders['SuccessResponse']['Body']['Orders']

def get_delivered_orders():
    delivered_orders = get_orders(ORDER_STATUS['delivered'])
    return delivered_orders['SuccessResponse']['Body']['Orders']

def get_returned_orders():
    returned_orders = get_orders(ORDER_STATUS['returned'])
    return returned_orders['SuccessResponse']['Body']['Orders']

def get_shipped_orders():
    shipped_orders = get_orders(ORDER_STATUS['shipped'])
    return shipped_orders['SuccessResponse']['Body']['Orders']

def get_failed_orders():
    failed_orders = get_orders(ORDER_STATUS['failed'])
    return failed_orders['SuccessResponse']['Body']['Orders']

def get_order_items(order_id):
    parameters = {
      'Action': ENDPOINT['GetOrderItems'],
      'Format':'json',
      'Timestamp': get_timestamp(),
      'UserID': settings.LAZADA_USER_ID,
      'Version': '1.0',
      'Status': 'pending',
      'OrderId': int(order_id)
    }

    parameters['Signature'] = generate_signature(parameters)
    res = requests.get(settings.LAZADA_ENDPOINT_URI, parameters)
    return json.loads(res.text)['SuccessResponse']['Body']['OrderItems']

def set_order_packed_by_marketplace(ordered_item_id):

    parameters = {
        'Action': ENDPOINT['SetStatusToPackedByMarketplace'],
        'Format':'json',
        'Timestamp': get_timestamp(),
        'UserID': settings.LAZADA_USER_ID,
        'Version': '1.0',
        'OrderItemIds': json.dumps([ordered_item_id]),
        'DeliveryType': 'dropship',
        'ShippingProvider': 'Hanoi%20Post%20-%20DO'
    }
    parameters['Signature'] = generate_signature(parameters)
    res = requests.get(settings.LAZADA_ENDPOINT_URI, parameters)
    try:
        res = json.loads(res.text)['SuccessResponse']['Body']['OrderItems'][0]
    except Exception as e:
        res = False
    return res

def set_order_ready_to_ship(order_id):
    dg = DeliveryGroup.objects.filter(order_id=order_id).first()

    if not dg:
        return False

    order_items = OrderedItem.objects.filter(delivery_group_id=dg.id).all()

    tracking_numbers = []
    # send packed_by_marketplace to get tracking numbers
    for item in order_items:
        tracking_number = set_order_packed_by_marketplace(item.lazada_order_item_id)
        if tracking_number:
            tracking_numbers.append(tracking_number)

    # update ordered item: set tracking number
    for order_item in order_items:
        for number in tracking_numbers:
            if order_item.lazada_order_item_id == str(number['OrderItemId']):
                order_item.lazada_tracking_number = number['TrackingNumber']
                order_item.save()
                break

    if tracking_numbers:

        for order_item in order_items:
            # set ready_to_ship
            parameters = {
                'Action': ENDPOINT['SetStatusToReadyToShip'],
                'Format':'json',
                'Timestamp': get_timestamp(),
                'UserID': settings.LAZADA_USER_ID,
                'Version': '1.0',
                'OrderId': int(order_id),
                'DeliveryType': 'dropship',
                'OrderItemIds': json.dumps([order_item.lazada_order_item_id]),
                'ShippingProvider': 'Hanoi%20Post%20-%20DO',
                'TrackingNumber': order_item.lazada_tracking_number
            }
            parameters['Signature'] = generate_signature(parameters)
            res = requests.get(settings.LAZADA_ENDPOINT_URI, parameters)

def sync_orders_from_lazada(orders):

    for order in orders:

        is_order_exists = True

        # check address exists
        billing_address =  Address.objects.filter(phone=order['AddressBilling']['Phone']).first()
        if not billing_address: 
            # create address
            street_address_1 = '{address1} {address5} {address4} {address3}'.format(address1=order['AddressBilling']['Address1'],
                address3=order['AddressBilling']['Address3'], address4=order['AddressBilling']['Address4'], address5=order['AddressBilling']['Address5'])
            
            billing_address = Address(first_name=order['CustomerFirstName'], last_name=order['CustomerLastName']
                , street_address_1=street_address_1, phone=order['AddressBilling']['Phone'], city=order['AddressBilling']['Address3'].replace(',',''))
            billing_address.save()
        # create user
        generated_email = 'lazada{phone}@gmail.com'.format(phone=order['AddressBilling']['Phone'])
        user = User.objects.filter(email=generated_email).first()
        if not user:
            user = User(email=generated_email, default_shipping_address=billing_address, default_billing_address=billing_address)
            user.save()
            user.addresses.add(billing_address)
        
        # create order
        order_obj = Order.objects.filter(lazada_order_id=order['OrderId'], user=user).first()
        if order_obj:
            if order_obj.status != order['Statuses'][0]:
                order_obj.status = order['Statuses'][0]
                order_obj.save()
                
        else:
            is_order_exists = False
            formated_price = Decimal(order['Price'].replace(',', ''))
            order_obj = Order(created=order['CreatedAt'] + '.069225+07', user=user, billing_address=billing_address,
                user_email=user.email, token=order['OrderNumber'], total_net=formated_price, total_tax=Decimal(0.00),
                lazada_order_id=order['OrderId'], status=order['Statuses'][0])
            order_obj.save()


        # create deveverygroup
        delivery_group = DeliveryGroup.objects.filter(order=order_obj).first()
        if not delivery_group:
            delivery_group = DeliveryGroup(order=order_obj, shipping_method_name='Dropshipping')
            delivery_group.save()

        # create order items
        order_items = get_order_items(order_obj.lazada_order_id)
        if not is_order_exists :
            for item in order_items:
                order_item = OrderedItem(product_name=item['Name'], product_sku=item['Sku'], quantity=1,
                    unit_price_net=item['ItemPrice'], unit_price_gross=item['ItemPrice'], delivery_group=delivery_group,
                    lazada_order_item_id=item['OrderItemId'])
                order_item.save()


def  util_sync_orders_status(request):
    
    orders = get_pending_orders() + get_ready_orders() + get_shipped_orders() + get_canceled_orders()

    return sync_orders_from_lazada(orders)
# def get_documents()