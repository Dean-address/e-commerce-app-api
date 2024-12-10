from django.urls import path
from user import views
from knox import views as knox_views

app_name = "user"
urlpatterns = [
    path("register/", views.Register.as_view(), name="otp"),
    path("verify/", views.VerifyUser.as_view(), name="otp-verification"),
    path("users/", views.UserList.as_view(), name="users"),
    path("user/<int:pk>/", views.UserDetail.as_view(), name="user-detail"),
    path("login/", views.Login.as_view(), name="knox_login"),
]
