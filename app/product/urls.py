from django.urls import path, include
from product import views
from rest_framework import routers


app_name = "product"

router = routers.SimpleRouter()
router.register("admin-products", views.AdminProductViewSet)
router.register("products", views.ProductViewSet)
router.register("cart", views.CartItemViewSet)
router.register("checkout", views.CheckoutViewSet, basename="checkout")
router.register("orders", views.OrderViewSet, basename="orders")
urlpatterns = [path("", include(router.urls))]
