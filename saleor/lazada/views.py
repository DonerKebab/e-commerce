from __future__ import unicode_literals
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from decimal import Decimal

from ..order.models import Order, DeliveryGroup, OrderedItem
from ..userprofile.models import Address, User
from .utils import get_pending_orders, get_order_items, set_order_ready_to_ship, get_all_orders


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
				, street_address_1=street_address_1, phone=order['AddressBilling']['Phone'], city=order['AddressBilling']['Address3'])
			billing_address.save()
		# create user
		generated_email = 'lazada{phone}@gmail.com'.format(phone=order['AddressBilling']['Phone'])
		user = User.objects.filter(email=generated_email).first()
		if not user:
			user = User(email=generated_email, default_shipping_address=billing_address, default_billing_address=billing_address)
			user.save()
			user.addresses.add(billing_address)
		
		# create order
		order_obj = Order.objects.filter(created=order['CreatedAt'] + '.069225+00', user=user).first()
		if not order_obj:
			is_order_exists = False
			formated_price = Decimal(order['Price'].replace(',', ''))
			order_obj = Order(status='pending', created=order['CreatedAt'] + '.069225+00', user=user, billing_address=billing_address,
				user_email=user.email, token=order['OrderNumber'], total_net=formated_price, total_tax=Decimal(0.00),
				lazada_order_id=order['OrderId'])
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
	return redirect('dashboard:orders')


def order_ready_to_ship(request, pk):

	set_order_ready_to_ship(pk)

	Order.objects.filter(pk=pk).update(status='ready_to_ship')

	return redirect('dashboard:orders')


def sync_pending_orders(request):
	orders = get_pending_orders()
	return sync_orders_from_lazada(orders)


def sync_all_orders(request):
	
	orders = get_all_orders()
	return sync_orders_from_lazada(orders)

