from django.urls import path
from .views import Buy, Sell, Cancel

urlpatterns = [
    path('order/buy', Buy.as_view(), name='register'),
    path('order/sell', Sell.as_view(), name='login'),
    path('order/cancel', Cancel.as_view(), name='logout'),
]