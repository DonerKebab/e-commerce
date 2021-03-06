from __future__ import unicode_literals
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from decimal import Decimal
from django.db.models import Q

from ..order.models import Order, DeliveryGroup, OrderedItem
from ..userprofile.models import Address, User
from .utils import get_order_items, set_order_ready_to_ship, get_pending_orders, get_canceled_orders, get_ready_orders,\
get_delivered_orders, get_returned_orders, get_shipped_orders, get_failed_orders, get_orders_by_id,  util_sync_orders_status
from .tasks import task_sync_lazada_orders




def order_ready_to_ship(request, pk):

    set_order_ready_to_ship(pk)

    Order.objects.filter(pk=pk).update(status='ready_to_ship')

    return redirect('dashboard:orders')


def sync_orders_status(request):
    task_sync_lazada_orders.delay()
    if request:
        return redirect('dashboard:orders')

def get_all_lazada_orders(request):
    orders = get_pending_orders() + get_ready_orders() + get_shipped_orders() + get_delivered_orders() + get_returned_orders() + get_failed_orders()
    return sync_orders_from_lazada(orders)
