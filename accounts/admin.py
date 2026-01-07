from blog.models import Article, Comment
from .models import User, UserProfile, Author, SocialLink
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from shop.models import Order, Book, Review
from home.admin import ControlAdmin, ControlInlineTabular, ControlInlineStacked


class UserProfileInline(ControlInlineStacked):
    model                 = UserProfile
    can_delete            = False
    extra                 = 0

    admin_editable_fields = ('status', 'profile_pic', 'author',)


class OrderInline(ControlInlineTabular):
    model            = Order
    fk_name          = 'user'
    extra            = 0
    can_delete       = False
    show_change_link = True

    readonly_fields  = ('order_number', 'status', 'total_amount', 'created_at')
    fields           = ('order_number', 'status', 'total_amount', 'created_at')


class SocialLinkInline(ControlInlineStacked):
    model                 = SocialLink
    extra                 = 0
    admin_editable_fields = ('facebook_url', 'x_url', 'youtube_url', 'linkedin_url', 'telegram_url', 'instagram_url', 'github_url')


class AuthorBookInline(ControlInlineTabular):
    model            = Book
    extra            = 0
    readonly_fields  = ('title', 'status', 'avg_rating', 'sales',)
    fields           = ('title', 'status', 'avg_rating', 'sales',)
    can_delete       = False
    show_change_link = True


class AuthorArticleInline(ControlInlineTabular):
    model            = Article
    extra            = 0
    readonly_fields  = ('title', 'status', 'created',)
    fields           = ('title', 'status', 'created',)
    can_delete       = False
    show_change_link = True


class ReviewInline(ControlInlineStacked):
    model                 = Review
    extra                 = 0
    readonly_fields       = ('date', 'book', 'stars',)
    fields                = ('book', 'stars', 'date', 'comment')
    can_delete            = True

    admin_editable_fields = ('comment',)

    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


class CommentInline(ControlInlineStacked):
    model                 = Comment
    extra                 = 0
    readonly_fields       = ('created', 'article',)
    fields                = ('article', 'created', 'message')
    can_delete            = True

    admin_editable_fields = ('message',)

    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


@admin.register(User)
class UserAdmin(ControlAdmin, BaseUserAdmin):
    model                 = User

    inlines               = [UserProfileInline, OrderInline, ReviewInline, CommentInline,]

    list_display          = ('username', 'number', 'email', 'is_staff', 'is_active', 'date_joined',)

    list_filter           = ('is_staff', 'is_active')
    search_fields         = ('username', 'number', 'email')
    ordering              = ('-date_joined',)
    readonly_fields       = ('date_joined',)

    admin_editable_fields = ('is_active',)

    fieldsets = (
        ('Account', {
            'fields': ('username', 'number', 'email', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Dates', {
            'fields': ('date_joined',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'number', 'email', 'password1', 'password2'),
        }),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()

        return super(UserAdmin, self).get_inline_instances(request, obj)


@admin.register(Author)
class AuthorAdmin(ControlAdmin):
    inlines               = [SocialLinkInline, AuthorBookInline, AuthorArticleInline]

    list_display          = ('full_name', 'status', 'demand', 'sale', 'total_books', 'total_articles')
    list_filter           = ('status', 'century',)
    search_fields         = ('first_name', 'last_name', 'user__username')
    readonly_fields       = ('slug', 'demand', 'sale', 'user')

    admin_editable_fields = ('status', 'century', 'first_name', 'last_name', 'bio',)

    fieldsets             = (
        ('Personal Info', {
            'fields': ('user', 'first_name', 'last_name', 'bio')
        }),
        ('Stats', {
            'fields': ('demand', 'sale', 'status')
        }),
        ('System', {
            'fields': ('slug',)
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = 'Author'

    def total_books(self, obj):
        return obj.books.count()

    total_books.short_description = 'Books'

    def total_articles(self, obj):
        return obj.articles.count()

    total_articles.short_description = 'Articles'