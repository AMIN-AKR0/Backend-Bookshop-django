from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# Create your models here.
class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, editable=False, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name)
            self.slug = slug
        
        super().save(*args, **kwargs)


class Article(models.Model):
    STATUS_CHOICES = [
        ('Public', 'Public' ),
        ('Waiting', 'Waiting' ),
    ]
    author   = models.ForeignKey('accounts.Author', on_delete=models.CASCADE, related_name='articles')
    title    = models.CharField(max_length=100)
    content  = models.TextField()
    created  = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='articles')
    slug     = models.SlugField(unique=True, editable=False, null=True)
    cover    = models.ImageField(upload_to='blog/article/cover')
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Public')

    def __str__(self):
        return f"{self.title} By {self.author}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug      = base_slug
            number    = 1
            
            while Article.objects.filter(slug=slug).exists():
                number += 1
                slug    = f"{base_slug}-{number}"
            
            self.slug = slug
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:article_page', kwargs={'slug': self.slug})


class ArticleView(models.Model):
    article     = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='views')
    ip_address  = models.GenericIPAddressField(db_index=True, null=True, blank=True)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    token       = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        unique_together = ('article', 'token')

    def __str__(self):
        return f"view {self.article.title} by {self.user.username}"


class ImageArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image   = models.ImageField(upload_to='blog/article/image')

    def clean(self):
        if self.article and self.article.images.count() >= 2:
            raise ValidationError("You can only upload at most 2 images")

    def __str__(self):
        return f'image for {self.article}'


class Comment(models.Model):
    user    = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} Comment by {self.article}"