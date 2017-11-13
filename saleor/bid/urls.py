from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'(?P<bid_session_id>[0-9-]+?)-(?P<product_id>[0-9]+)/getprice/$',
        views.get_newest_bid_price, name="get-bid-price"),
    url(r'^bidprice/$',
        views.bid_product, name="bid-price")

    ]
