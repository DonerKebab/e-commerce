from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^sync_lazada_orders/$',
        views.sync_all_orders, name="sync-lazada-orders"),

    url(r'^sync_pending_lazada_orders/$',
        views.sync_pending_orders, name="sync-pending-lazada-orders"),

    url(r'^(?P<pk>[0-9]+)/ready$',
        views.order_ready_to_ship, name="order-ready-to-ship"),
    
    ]