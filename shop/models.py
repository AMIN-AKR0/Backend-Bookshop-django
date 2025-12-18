import uuid
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import DecimalField
from django.utils import timezone
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
    image        = models.ImageField(upload_to='books/')
    created_at   = models.DateTimeField(auto_now_add=True)
    sales        = models.IntegerField(default=0, editable=False)


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

    def get_total_price(self):
        total = 0
        for item in self.items.all():
            total += item.book.price * item.quantity

        return total

    def get_taxes(self):
        total = self.get_total_price()
        return total / 100

    def get_final_price(self):
        total = self.get_total_price()
        taxes = self.get_taxes()

        return total + taxes


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

    def get_item_price(self):
        return self.book.price * self.quantity


class CheckOutData(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkout_data')
    name        = models.CharField(max_length=41)
    number      = models.CharField(max_length=11)
    address     = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20)
    token       = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() - self.created_at > timedelta(hours=1)


class Order(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Shipped', 'Shipped'),
        ('Transmitted', 'Transmitted'),
        ('Canceled', 'Canceled'),
        ('Completed', 'Completed'),
    ]

    user          = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    order_number  = models.CharField(max_length=29, unique=True)
    customer_name = models.CharField(max_length=100)
    phone_number1 = models.CharField(max_length=11)
    phone_number2 = models.CharField(max_length=11)
    address       = models.TextField()
    postal_code   = models.CharField(max_length=20)
    total_amount  = DecimalField(max_digits=10, decimal_places=2)
    created_at    = models.DateTimeField(auto_now_add=True)
    paid_at       = models.DateTimeField(null=True, blank=True)
    status        = models.CharField(max_length=30, choices=STATUS_CHOICES, default='paid')
    payment_id    = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email         = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f'order by {self.user.username} at {self.created_at}'

    def get_total_price(self):
        return self.total_amount - (self.total_amount % 100)

    def get_taxes(self):
        return self.get_total_price() / 100


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book     = models.ForeignKey(Book, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.book} * {self.quantity} for {self.order.user.username}'