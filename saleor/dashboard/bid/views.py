from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import pgettext_lazy
from django.shortcuts import get_object_or_404, redirect
from decimal import Decimal
from django.utils import timezone

from ...bid.models import BidSession, ProductBidHistory
from ...bid.utils import create_random_name
from ..views import staff_member_required
from . import forms


@staff_member_required
def bid_list(request):
    bids = BidSession.objects.filter(end_bid__gte=timezone.now()).prefetch_related('products')
    ctx = {'bids': bids}
    return TemplateResponse(request, 'dashboard/bid/bid_list.html', ctx)

@staff_member_required
def bid_edit(request, pk=None):
    if pk:
        instance = get_object_or_404(BidSession, pk=pk)
    else:
        instance = BidSession()
    form = forms.BidSessionForm(
        request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save()
        # if create new bids then create ProductBidHistory for each product
        if not pk:
            for product in instance.products.all():
                bid_history = create_bid_history(instance, product)
                if bid_history:
                    rs = ProductBidHistory.objects.bulk_create(bid_history) 
        msg = pgettext_lazy(
            'Bid message', 'Updated bid') if pk else pgettext_lazy(
                'Bid message', 'Added bid')
        messages.success(request, msg)
        return redirect('dashboard:bid-update', pk=instance.pk)
    ctx = {'bid': instance, 'form': form}
    return TemplateResponse(request, 'dashboard/bid/bid_form.html', ctx)

@staff_member_required
def clone_bid(request, pk=None):
    clone_object = BidSession()
    if pk:
        instance = get_object_or_404(BidSession, pk=pk)
        bid_time = (instance.end_bid - instance.start_bid).total_seconds()
        # start next bid session in 120 seconds 
        next_start_bid = instance.end_bid + timezone.timedelta(seconds=120)
        next_end_bid = next_start_bid + timezone.timedelta(seconds=bid_time)
        clone_object = BidSession(name=instance.name, start_bid=next_start_bid, end_bid=next_end_bid)
        clone_object.save()
        for product in instance.products.all():
            clone_object.products.add(product)

        for product in clone_object.products.all():
                bid_history = create_bid_history(clone_object, product)
                if bid_history:
                    rs = ProductBidHistory.objects.bulk_create(bid_history)
        messages.success(request, 'Clone đấu giá thành công')
    return redirect('dashboard:bid-update', pk=clone_object.id)


@staff_member_required
def bid_delete(request, pk):
    bid_session = get_object_or_404(BidSession, pk=pk)
    if request.method == 'POST':
        bid_session.delete()
        messages.success(
            request,
            pgettext_lazy('Dashboard message', 'Deleted bid session %s') % bid_session)
        return redirect('dashboard:bid-list')
    return TemplateResponse(
        request, 'dashboard/bid/bid_modal_confirm_delete.html',
        {'bid_session': bid_session})

def create_bid_history(bid, product):
    bid_history = []
    start_bid_price = Decimal(1000.00)
    step = Decimal(5000.00)

    bid_time = int((bid.end_bid - bid.start_bid).total_seconds())
    time_bot_bidding = int(bid_time * 0.75)
    max_price_bot_bid = Decimal(product.price.net) * Decimal(0.75)

    num_time_bot_bid = int(max_price_bot_bid / step)
    num_seconds_to_next_bid = time_bot_bidding / num_time_bot_bid

    for i in range(1, num_time_bot_bid):
        
        bid_price = step * i + start_bid_price
        bid_time = bid.start_bid + timezone.timedelta(seconds=(i*num_seconds_to_next_bid))
        user_display_name = create_random_name()

        bid_history.append(ProductBidHistory(session_id=bid.id, product_id=product.id, user_id=1
            , bid_price=bid_price, bid_time=bid_time, user_display_name=user_display_name))

    return bid_history


