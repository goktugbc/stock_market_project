from django.utils import timezone
from datetime import timedelta
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from midas_case.rest_framework_settings import CsrfExemptSessionAuthentication
from midas_case.models import Order
from .serializers import BuyOrderCreateSerializer, SellOrderCreateSerializer, CancelOrderSerializer, OrderSerializer
from ...event_streamer import EventStreamer


class Buy(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = BuyOrderCreateSerializer

    @swagger_auto_schema(request_body=BuyOrderCreateSerializer)
    def post(self, request):
        request.data['user'] = request.user.pk
        serializer = BuyOrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Sell(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = SellOrderCreateSerializer

    @swagger_auto_schema(request_body=SellOrderCreateSerializer)
    def post(self, request):
        request.data['user'] = request.user.pk
        serializer = SellOrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Cancel(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = CancelOrderSerializer

    @swagger_auto_schema(request_body=CancelOrderSerializer)
    def delete(self, request):
        from midas_case.celery import buy, cancel
        try:
            order = Order.objects.get(id=request.data["id"])
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        event_streamer = EventStreamer("cancel")
        event_streamer.create_producer()
        event_streamer.send_message({"id": str(order.id)})
        buy.apply_async(args=[], serializer="json", eta=timezone.now() + timedelta(seconds=10))
        cancel.apply_async(args=[], serializer="json", eta=timezone.now() + timedelta(seconds=10))
        return Response(status=status.HTTP_202_ACCEPTED)


class RetrieveOrder(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        if order.user == request.user:
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        else:
            return Response({'msg': 'Wrong user.'}, status=status.HTTP_403_FORBIDDEN)


class RetrieveOrdersOfUser(generics.ListAPIView):
    serializer_class = OrderSerializer
    model = Order

    @swagger_auto_schema(request_body=OrderSerializer)
    def get_queryset(self):
        user = self.request.user
        queryset = self.model.objects.filter(user=user)
        return queryset
