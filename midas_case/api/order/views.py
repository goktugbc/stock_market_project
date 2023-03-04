import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from midas_case.rest_framework_settings import CsrfExemptSessionAuthentication
from midas_case.models import Order
from .serializers import BuyOrderCreateSerializer, SellOrderCreateSerializer, CancelOrderSerializer
from ...event_streamer import EventStreamer


class Buy(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = BuyOrderCreateSerializer

    def post(self, request):
        from midas_case.celery import buy, sell
        request.data['user'] = request.user.pk
        serializer = BuyOrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            buy.apply_async(args=[], serializer="json")
            sell.apply_async(args=[], serializer="json")
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Sell(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = SellOrderCreateSerializer

    def post(self, request):
        from midas_case.celery import buy, sell
        serializer = SellOrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            buy.apply_async(args=[], serializer="json")
            sell.apply_async(args=[], serializer="json")
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Cancel(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = CancelOrderSerializer

    def delete(self, request):
        from midas_case.celery import buy, sell, cancel
        try:
            order = Order.objects.get(id=request.data["id"])
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        event_streamer = EventStreamer("cancel")
        event_streamer.create_producer()
        event_streamer.send_message({"id": str(order.id)})
        buy.apply_async(args=[], serializer="json")
        sell.apply_async(args=[], serializer="json")
        cancel.apply_async(args=[], serializer="json")
        return Response(status=status.HTTP_202_ACCEPTED)
