import os
import uuid
from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def product_image_file_path(instance, filename):

    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads", "products", filename)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **other_fields):
        """Create and save a new user"""
        if not email:
            return ValueError("User must have an email address.")
        user = self.model(
            email=self.normalize_email(email), username=username, **other_fields
        )
        user.is_active = False
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password=None, username=None):
        """Create and save a superuser"""
        user = self.create_user(email, password, username="")
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """User in the system"""

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.IntegerField(null=True)
    image = models.ImageField(null=True, upload_to=product_image_file_path)

    def __str__(self):
        return self.name
