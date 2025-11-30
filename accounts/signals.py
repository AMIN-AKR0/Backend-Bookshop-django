from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, UserProfile
from shop.models import Cart

@receiver(post_save, sender=User)
def creat_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def creat_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)