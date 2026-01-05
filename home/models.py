from django.db import models

# Create your models here.
class SiteSettings(models.Model):
    site_name              = models.CharField(max_length=100, default="Bookim")
    facebook               = models.URLField(default="https://www.facebook.com", blank=True, null=True)
    x                      = models.URLField(default="https://x.com", blank=True, null=True)
    instagram              = models.URLField(default="https://www.instagram.com/bookim", blank=True, null=True)
    linkedin               = models.URLField(default="https://www.linkedin.com", blank=True, null=True)
    telegram               = models.URLField(default="https://www.telegram.org/bookim", blank=True, null=True)
    email                  = models.EmailField(default="bookim.bookshop@gmail.com")

    def __str__(self):
        return 'Site Settings'