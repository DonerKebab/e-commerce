from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.bid_list, name='bid-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.bid_edit, name='bid-update'),
    url(r'^add/$', views.bid_edit, name='bid-add'),
    url(r'^clone/(?P<pk>[0-9]+)/$', views.clone_bid, name='bid-clone'),
    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.bid_delete, name='bid-delete'),
    ]