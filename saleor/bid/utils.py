from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from .models import BidSession, ProductBidHistory


def bid_session_for_homepage():
	user = AnonymousUser()
	now = timezone.now()
	bid_session  = BidSession.objects.filter(end_bid__gte=now,
                                start_bid__lte=now).first()
	return bid_session
