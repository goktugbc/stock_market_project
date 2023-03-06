from django.urls import path, re_path
from .views import Buy, Sell, Cancel, RetrieveOrder, RetrieveOrdersOfUser

urlpatterns = [
    path('order/buy', Buy.as_view(), name='buy'),
    path('order/sell', Sell.as_view(), name='sell'),
    path('order/cancel', Cancel.as_view(), name='cancel'),
    re_path('^order/(?P<order_id>[0-9a-zA-Z_-]+)/', RetrieveOrder.as_view(), name='retrieve_order'),
    path('orders', RetrieveOrdersOfUser.as_view(), name='retrieve_orders'),
]