from core.models import Product, Cart, CartItem
from product.serializers import ProductSerializer, CartSerializer, CartItemSerializer
from rest_framework import permissions, viewsets, mixins, status
from rest_framework.response import Response
from knox.auth import TokenAuthentication


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


# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     # serializer_class = CartSerializer
#     # def retrieve


class CartItemViewSet(viewsets.ModelViewSet):
    """View to manage cart items"""

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
