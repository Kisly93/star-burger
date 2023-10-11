from rest_framework.serializers import ModelSerializer
from .models import OrderItem, Order

class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)
    class Meta:
        model = Order
        fields = ['id','firstname', 'lastname', 'address', 'phonenumber', 'products']
