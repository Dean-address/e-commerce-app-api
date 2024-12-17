from core.models import Product, Cart, CartItem, Order, OrderItem
from product.serializers import (
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
)
from rest_framework import permissions, viewsets, mixins, status
from rest_framework.response import Response
from knox.auth import TokenAuthentication
from django.db import transaction


class AdminProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """View for Admin to Manage product"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]


class ProductViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """View for authenticated user to view list of product avaiable"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class CartItemViewSet(viewsets.ModelViewSet):
    """View for authenticated user to manage carts"""

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = CartItem.objects.filter(cart__user=user)
        return queryset

    def create(self, request):
        user = request.user
        # Get or create a cart for the User
        cart, created = Cart.objects.get_or_create(user=user)
        # Get data from request
        product_id = request.data.get("product")
        quantity = request.data.get("quantity")

        if not product_id and quantity:
            return Response(
                {"detail": "Product and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Fetch the Product instance by ID
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        cartItem = CartItem.objects.get_or_create(
            cart=cart, product=product, quantity=quantity
        )
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CheckoutViewSet(viewsets.ModelViewSet):
    """View for authenticated user to manage orders"""

    queryset = Order.objects.none()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
            cartItem = CartItem.objects.filter(cart=cart)

            if not cartItem.exists():
                return Response(
                    {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                total_price = sum(item.total_price for item in cartItem)
                order = Order.objects.create(user=user, total_price=total_price)
                for item in cartItem:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                    )
                cartItem.delete()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )


class OrderViewSet(viewsets.ModelViewSet):
    """Manage orders for a user"""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(user=user)
        return queryset
