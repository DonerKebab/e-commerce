from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import pgettext_lazy
from django.shortcuts import get_object_or_404, redirect

from ...bid.models import BidSession
from ..views import staff_member_required
from . import forms


@staff_member_required
def bid_list(request):
    bids = BidSession.objects.prefetch_related('products')
    for bid in bids:
        print(bid.products.all())
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
        msg = pgettext_lazy(
            'Bid message', 'Updated bid') if pk else pgettext_lazy(
                'Bid message', 'Added bid')
        messages.success(request, msg)
        return redirect('dashboard:bid-update', pk=instance.pk)
    ctx = {'bid': instance, 'form': form}
    return TemplateResponse(request, 'dashboard/bid/bid_form.html', ctx)