from rest_framework import serializers

from core.models import CustomUser
from django.contrib.auth import authenticate

from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "password"]
        extra_kwargs = {
            "password": {
                "write_only": True
            }  # Ensure the password is not included in the response
        }

    def create(self, validated_data):
        # Ensure the hashed password is saved
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.is_active = False
        user.save()
        return user


class OtpSerializer(serializers.Serializer):
    otp = serializers.CharField()


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), username=email, password=password
            )
            if not user:
                raise serializers.ValidationError(
                    {"detail": _("Invalid email or password.")},
                    code="authorization",
                )
        else:
            raise serializers.ValidationError(
                {"detail": _("Must include both email and password.")},
                code="authorization",
            )

        data["user"] = user
        return data
