from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from midas_case.models import Order
from midas_case.constants import BUY_ORDER, SELL_ORDER


class BuyOrderCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    user = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'planned_number_of_apples']

    def save(self):
        order = Order(user_id=self.validated_data['user'], type=BUY_ORDER,
                      planned_number_of_apples=self.validated_data['planned_number_of_apples'])
        order.save()
        return order


class SellOrderCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    user = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'planned_number_of_apples']

    def save(self):
        order = Order(user_id=self.validated_data['user'], type=SELL_ORDER,
                      planned_number_of_apples=self.validated_data['planned_number_of_apples'])
        order.save()
        return order


class CancelOrderSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()

    class Meta:
        model = Order
        fields = ['id']

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'type', 'planned_number_of_apples', 'actual_number_of_apples', 'create_datetime', 'closed_datetime',
                  'closed', 'cancelled', 'result']
