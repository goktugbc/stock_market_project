from rest_framework import serializers
from midas_case.models import Order
from midas_case.constants import BUY_ORDER, SELL_ORDER


class BuyOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['type', 'planned_number_of_apples']

    def save(self):
        order = Order(user=self.context['request'].user, type=BUY_ORDER,
                      planned_number_of_apples=self.validated_data['planned_number_of_apples'])
        order.save()
        return order


class SellOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['type', 'planned_number_of_apples']

    def save(self):
        order = Order(user=self.context['request'].user, type=SELL_ORDER,
                      planned_number_of_apples=self.validated_data['planned_number_of_apples'])
        order.save()
        return order


class CancelOrderSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
