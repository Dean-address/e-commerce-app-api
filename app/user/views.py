from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib.auth import get_user_model


from core.models import CustomUser
from user.serializers import UserSerializer, OtpSerializer, AuthTokenSerializer

from knox.models import AuthToken
import pyotp

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import permissions, generics, status
from rest_framework.exceptions import AuthenticationFailed


def generate_otp():
    secret_key = pyotp.random_base32()
    otp = pyotp.TOTP(secret_key, interval=60)
    return otp.now()


class Register(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = request.data["email"]
            otp = generate_otp()
            try:
                send_mail(
                    "Ecommerce OTP CODE",
                    f"{otp} is you otp code and expires in 120 seconds",
                    "emailtest119@yahoo.com",
                    [f"{email}"],
                    fail_silently=True,
                )
                cache.set("otp", otp, timeout=120)
                cache.set("email", email)
            except Exception as e:
                raise ValidationError({"email": f"Failed to send OTP: {str(e)}"})
            else:

                user = serializer.save()
                print(user.password)  # Check hashed password
                print(user.check_password(request.data["password"]))
                return Response(
                    {
                        "message": "OTP sent successfully. Please verify within 120 seconds.",
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUser(generics.GenericAPIView):
    serializer_class = OtpSerializer
    queryset = CustomUser

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        otp = request.data.get("otp")

        cached_otp = cache.get("otp")
        cached_email = cache.get("email")
        if not cached_otp:
            raise ValidationError({"otp": "OTP expired or invalid."})

        if str(cached_otp) != str(otp):
            raise ValidationError({"otp": "Incorrect OTP."})

        user = get_user_model().objects.get(email=cached_email)
        if user:
            user.is_active = True
            user.save()
            cache.delete("otp")
            cache.delete("email")
            return Response(
                {"message": "User verified successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


class Login(generics.GenericAPIView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        # Validate the serializer with the request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated user
        user = serializer.validated_data["user"]
        if not user:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate token using Knox
        token = AuthToken.objects.create(user)[1]

        # Return user info and token
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": token,
            },
            status=status.HTTP_200_OK,
        )


class UserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
