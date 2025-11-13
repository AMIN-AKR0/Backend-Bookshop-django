from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.db import models

from accounts.managers import UserManager


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email        = models.EmailField(unique=True)
    number       = models.CharField(max_length=12, unique=True, null=True, blank=True)
    username     = models.CharField(max_length=30, unique=True)
    date_joined  = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['number', 'username']


    objects = UserManager()


    def __str__(self):
        return self.username

