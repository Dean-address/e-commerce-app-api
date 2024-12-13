from django.urls import path
from product.views import ProductList, ProductDetail, Products


app_name = "product"
urlpatterns = [
    path("product/", ProductList.as_view(), name="product_list"),
    path("product/<int:pk>/", ProductDetail.as_view(), name="product_detail"),
    path("products/", Products.as_view(), name="products"),
]
