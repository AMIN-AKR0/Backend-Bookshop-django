from datetime import timedelta
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
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


class UserProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', editable=False)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pics')
    date_joined = models.DateTimeField(auto_now_add=True)
    author      = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"profile for {self.user.number}"

    def save(self, *args, **kwargs):
        if self.author and not Author.objects.filter(user=self.user).exists():
            Author.objects.create(user=self.user)
            
        super().save(*args, **kwargs)


class Author(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author')
    first_name = models.CharField(max_length=30)
    last_name  = models.CharField(max_length=30)
    bio        = models.TextField(null=True, blank=True)
    century    = models.ForeignKey('shop.Century', related_name='author', blank=True, null=True, on_delete=models.SET_NULL)
    slug       = models.SlugField(unique=True, editable=False)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.first_name} {self.last_name}")
            slug      = base_slug
            number    = 1
            while Author.objects.filter(slug=slug).exists():
                number += 1
                slug    = f"{base_slug}-{number}"

            self.slug = slug

        super().save(*args, **kwargs)


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


class SocialLink(models.Model):
    author        = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='social_links')
    facebook_url  = models.URLField(null=True, blank=True)
    x_url         = models.URLField(null=True, blank=True)
    youtube_url   = models.URLField(null=True, blank=True)
    linkedin_url  = models.URLField(null=True, blank=True)
    telegram_url  = models.URLField(null=True, blank=True)
    github_url    = models.URLField(null=True, blank=True)
    instagram_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'links for {self.author.user.username}'