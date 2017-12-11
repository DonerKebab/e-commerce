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

from ..order.models import DeliveryGroup, Order, OrderedItem

ENDPOINT = {
    'GetOrders': 'GetOrders',
    'GetOrderItems': 'GetOrderItems',
    'SetStatusToPackedByMarketplace': 'SetStatusToPackedByMarketplace',
    'SetStatusToReadyToShip': 'SetStatusToReadyToShip',
    'GetDocument': 'GetDocument'
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
        for number in tracking_numers:
            if order_item.lazada_order_item_id == str(number['OrderItemId']):
                order_item.lazada_tracking_number = number['TrackingNumber']
                order_item.save()
                break

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


# def get_documents()