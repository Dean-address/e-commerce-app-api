from rest_framework import serializers
from core.models import Product, CartItem, Cart


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "quantity", "image"]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"
        read_only_fields = ["created_at"]


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        # fields = ["cart", "product", "quantity", "added_at"]
        fields = "__all__"
        read_only_fields = ["added_at"]
