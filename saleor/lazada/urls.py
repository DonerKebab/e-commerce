from django.conf.urls import url

from . import views


urlpatterns = [

    url(r'^sync_lazada_orders/$',
        views.sync_orders_status, name="sync-lazada-orders"),
    url(r'^sync_all_lazada_orders/$',
        views.get_all_lazada_orders, name="sync-all-lazada-orders"),
    url(r'^(?P<pk>[0-9]+)/lazadaready$',
        views.order_ready_to_ship, name="lazada-order-ready-to-ship"),
    ]