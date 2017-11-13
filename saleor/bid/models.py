from __future__ import unicode_literals
from django.db import models
from django_prices.models import PriceField

from django.conf import settings
from django.utils.translation import pgettext, pgettext_lazy
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils import timezone


@python_2_unicode_compatible
class BidSession(models.Model):

    name = models.CharField(pgettext_lazy('Bid session field', 'name'), max_length=255)
    products = models.ManyToManyField('product.Product')
    start_bid = models.DateTimeField(
        pgettext_lazy('Bid session field', 'Start bid time'),
        default=timezone.now)
    end_bid = models.DateTimeField(
        pgettext_lazy('Bid session field', 'End bid time'),
        default=timezone.now() + timezone.timedelta(hours=1))

    def __repr__(self):
        return 'Bid(name=%r)' % (str(self.name))

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class ProductBidHistory(models.Model):
    
    session = models.ForeignKey('bid.BidSession')
    product = models.ForeignKey('product.Product')
    user = models.ForeignKey('userprofile.user')
    bid_price = PriceField(
        pgettext_lazy('Product bid session history field', 'bid price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2)
    bid_time = models.DateTimeField(
        pgettext_lazy('Product bid session history field', 'bid time'),
        default=timezone.now, editable=False)
    user_display_name = models.CharField(max_length=255, blank=True, null=True)