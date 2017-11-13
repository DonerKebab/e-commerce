from __future__ import unicode_literals
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from decimal import Decimal

from ..registration.forms import LoginForm
from ..product.models import Product
from .models import ProductBidHistory, BidSession



def get_newest_bid_price(request, bid_session_id, product_id):

    bid_history = ProductBidHistory.objects.filter(product_id=product_id, session_id=bid_session_id).order_by("-bid_price").first()
    product = get_object_or_404(Product, pk=product_id)
    bid_session = get_object_or_404(BidSession, pk=bid_session_id)

    if not bid_history:
        bid_info = {'current_price': product.start_bid_price.net, 'winner': '', 'end_bid': bid_session.end_bid.isoformat()}
    else:
        bid_info = {'current_price': bid_history.bid_price.net, 'winner': bid_history.user_display_name, 'current_winner': False, 'end_bid': bid_session.end_bid.isoformat()}

        # check if request.user is current winner
        if request.user.id == bid_history.user_id:
            bid_info['current_winner'] = True

    if bid_session.end_bid < timezone.now():
        bid_info['isEnd'] = True
        if bid_history and bid_history.user_id == request.user.id:
            bid_info['isWin'] = True
        else:
            bid_info['isWin'] = False
    else:
        bid_info['isEnd'] = False


    return JsonResponse(bid_info, status=200)


def bid_product(request):

    # check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('social:begin', 'facebook')

    if not request.method == 'POST':
        return redirect(reverse(
            'product:details',
            kwargs={'product_id': product_id, 'slug': slug}))

    bid_session_id = request.POST['bid_session_id']
    bid_price = request.POST['bid_price']
    product_id = request.POST['product_id']
    user = request.user
    user_displayname = user.email[:user.email.index("@")]
    
    product = get_object_or_404(Product, id=product_id)
    # check if bid session is expiered or has not ready yet
    bid_session = get_object_or_404(BidSession, id=bid_session_id)
    if bid_session.end_bid < timezone.now() or bid_session.start_bid > timezone.now():
        return redirect(reverse(
            'product:details',
            kwargs={'product_id': product_id, 'slug': product.get_slug()}))

    
    # check if bid price is valid: not under current price, if bidding user is current winner user
    current_bid_winner = ProductBidHistory.objects.filter(product_id=product_id, session_id=bid_session_id).order_by('-bid_price').first()
    
    if current_bid_winner:
        if(current_bid_winner.user_id == user.id):
            return JsonResponse({'message': 'Bạn đang là người giữ giá cao nhất của sản phẩm này.'}, status=200)

        if(int(bid_price) < int(current_bid_winner.bid_price.net)): 
            return JsonResponse({'message': 'Giá thầu không hợp lệ.'}, status=200)   

    # add to bid product history
    pbh = ProductBidHistory.objects.create(product_id=product_id, session_id=bid_session_id, bid_price=int(bid_price)
        ,user_id=request.user.id, user_display_name=user_displayname)    

    if int(product.price.net) - int(bid_price) <= 5000:
        bid_session.end_bid = timezone.now()
        bid_session.save()
    return redirect(reverse(
            'product:details',
            kwargs={'product_id': product_id, 'slug': product.get_slug()}))
