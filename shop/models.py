from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db import models
from django.urls import reverse
from accounts.models import User, UserProfile, Author


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug      = base_slug
            number    = 1
            while Tag.objects.filter(slug=slug).exists():
                number   += 1
                slug      = f"{base_slug}-{number}"

            self.slug = slug
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            number = 1
            while Category.objects.filter(slug=slug).exists():
                number += 1
                slug = f"{base_slug}-{number}"
            self.slug = slug
        super().save(*args, **kwargs)


class Century(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OnlineStore(models.Model):
    name  = models.CharField(max_length=100)
    image = models.ImageField(upload_to='online_store/')
    url   = models.URLField()

    def __str__(self):
        return self.name


class Book(models.Model):
    title        = models.CharField(max_length=100)
    description  = models.TextField()
    price        = models.FloatField()
    summary      = models.TextField(null=True, blank=True)
    sku          = models.CharField(max_length=300)
    pages        = models.IntegerField()
    publish_year = models.IntegerField(null=True, blank=True)
    publish_date = models.DateField(null=True, blank=True)
    language     = models.CharField(max_length=100)
    dimensions	 = models.CharField(max_length=300, null=True, blank=True)
    weight       = models.CharField(max_length=300, null=True, blank=True)
    author       = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    slug         = models.SlugField(max_length=300, unique=True, null=True, blank=True, editable=False)
    tags         = models.ManyToManyField(Tag, related_name='books', blank=True)
    categories   = models.ForeignKey(Category, related_name='books', on_delete=models.SET_NULL, null=True, blank=True)
    century      = models.ForeignKey(Century, related_name='books', blank=True, null=True, on_delete=models.SET_NULL, editable=False)
    online_store = models.ManyToManyField(OnlineStore, related_name='books', blank=True)
    avg_rating   = models.FloatField(default=0, editable=False)
    image        = models.ImageField(upload_to='books/', null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug      = base_slug
            number    = 1
            while Book.objects.filter(slug=slug).exists():
                number   += 1
                slug      = f"{base_slug}-{number}"

            self.slug = slug

        self.century  = self.author.century

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:book-detail', kwargs={'slug': self.slug})


class Review(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book    = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    stars   = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    date    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"review by {self.user.username} for {self.book.title}"

    def save(self, *args, **kwargs):
        if int(self.stars) > 5:
            self.stars = 5
        elif int(self.stars) < 1:
            self.stars = 1

        reviews = self.book.reviews.all()
        users   = [self.user.id]
        stars   = 0

        for review in reviews:
            if review.user.id not in users:
                stars += review.stars
                users.append(review.user.id)

        stars += int(self.stars)

        avg = stars / len(users)
        self.book.avg_rating = avg
        self.book.save()
        super().save(*args, **kwargs)

    def delete(self, **kwargs):
        reviews = self.book.reviews.all()
        users   = [self.user.id]
        stars   = 0

        for review in reviews:
            if review.user.id not in users:
                stars += review.stars
                users.append(review.user.id)

        if len(users) == 1:
            users.append(0)

        avg = stars / (len(users) - 1)
        self.book.avg_rating = avg
        self.book.save()
        super().delete(**kwargs)


class Cart(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    books = models.ManyToManyField(Book, blank=True, through="CartItem")

    def __str__(self):
        return f"cart for {self.user.username}"


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book     = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(30)])

    class Meta:
        unique_together = ('cart', 'book')

    def __str__(self):
        return f"{self.book} in {self.cart.user.username} cart"

    def save(self, *args, **kwargs):
        if self.quantity < 1:
            self.quantity = 1

        if self.quantity > 30:
            self.quantity = 30

        super().save(*args, **kwargs)