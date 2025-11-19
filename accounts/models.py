from datetime import timedelta

from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from accounts.managers import UserManager


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email        = models.EmailField(unique=True, null=True, blank=True)
    number       = models.CharField(max_length=11, unique=True)
    username     = models.CharField(max_length=30, unique=True)
    date_joined  = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)

    USERNAME_FIELD  = 'number'
    REQUIRED_FIELDS = ['email', 'username']


    objects = UserManager()


    def __str__(self):
        return self.username


class Register(models.Model):
    phone_number = models.CharField(unique=True, max_length=11)
    code         = models.CharField(max_length=5)
    time         = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        now = timezone.now()

        if timedelta(minutes=2) < now - self.time:
            return True
        else:
            return False

    def delete_expired(self):
        if self.is_expired():
            self.delete()