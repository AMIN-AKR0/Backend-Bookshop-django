from django.contrib import admin
from home.admin import ControlAdmin, ControlInlineTabular
from .models import Book, Order, OrderItem, Tag, Category, Century, OnlineStore, Review

class ReviewInline(ControlInlineTabular):
    model            = Review
    extra            = 0
    readonly_fields  = ('date', 'book', 'stars')
    fields           = ('book', 'stars', 'date', 'comment')
    can_delete       = True
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


class OrderItemInline(ControlInlineTabular):
    model           = OrderItem
    extra           = 0
    can_delete      = False
    readonly_fields = ('book', 'quantity', 'price')
    fields          = ('book', 'quantity', 'price')


class BookOrderItemInline(ControlInlineTabular):
    model               = OrderItem
    extra               = 0
    can_delete          = False
    verbose_name        = "Sold Item"
    verbose_name_plural = "Sales History"

    fields              = ('order', 'quantity', 'price',)

    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


class OrderInline(ControlInlineTabular):
    model            = Order
    extra            = 0
    can_delete       = False
    show_change_link = True
    readonly_fields  = ('order_number', 'status', 'total_amount', 'created_at')
    fields           = ('order_number', 'status', 'total_amount', 'created_at')


@admin.register(Book)
class BookAdmin(ControlAdmin):
    model                 = Book

    inlines               = [ReviewInline, BookOrderItemInline]

    admin_editable_fields = ('status', 'description', 'summary', 'image', 'number')

    list_display          = ('title', 'author', 'price', 'status', 'number',)

    readonly_fields        = ('author', 'avg_rating', 'sales', 'slug',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'author', 'categories', 'tags', 'century')
        }),
        ('Details', {
            'fields': ('description', 'summary', 'price', 'sku', 'publish_year')
        }),
        ('System', {
            'fields': ('slug', 'avg_rating', 'sales', 'status', 'image', 'number')
        }),
    )

    list_filter = ('status', 'categories', 'century', 'tags')

    ordering = ('-created_at',)


@admin.register(Order)
class OrderAdmin(ControlAdmin):
    model                 = Order

    inlines               = [OrderItemInline]

    admin_editable_fields = ('status', 'address', 'postal_code',)

    list_display          = ('order_number', 'user_name', 'status', 'total_amount', 'created_at', 'paid_at')
    list_filter           = ('status', 'created_at', 'paid_at')
    search_fields         = ('order_number', 'user__username', 'customer_name', 'phone_number1', 'phone_number2')
    readonly_fields       = ('order_number', 'total_amount', 'created_at', 'paid_at', 'payment_id')
    ordering              = ('-created_at',)

    fieldsets             = (
        ('Customer Info', {
            'fields': ('user', 'customer_name', 'phone_number1', 'phone_number2', 'address', 'postal_code', 'email')
        }),
        ('Order Details', {
            'fields': ('order_number', 'total_amount', 'status', 'payment_id', 'created_at', 'paid_at')
        }),
    )

    def user_name(self, obj):
        return obj.user.username

    user_name.short_description = 'User'


@admin.register(Tag)
class TagAdmin(ControlAdmin):
    list_display          = ('name', 'slug')
    readonly_fields       = ('slug',)
    search_fields         = ('name',)

    admin_editable_fields = ('name',)

    def has_add_permission(self, request):
        return self.is_admin(request)

    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)

    def has_change_permission(self, request, obj=None):
        return self.is_owner(request)


@admin.register(Category)
class CategoryAdmin(ControlAdmin):
    list_display          = ('name', 'slug')
    readonly_fields       = ('slug',)
    search_fields         = ('name',)

    admin_editable_fields = ('name',)

    def has_add_permission(self, request):
        return self.is_admin(request)

    def has_change_permission(self, request, obj=None):
        return self.is_owner(request)


@admin.register(Century)
class CenturyAdmin(ControlAdmin):
    list_display  = ('name',)
    search_fields = ('name',)

    def has_module_permission(self, request):
        return self.is_owner(request)


@admin.register(OnlineStore)
class OnlineStoreAdmin(ControlAdmin):
    list_display  = ('name', 'url', 'image')
    search_fields = ('name',)

    def has_module_permission(self, request):
        return self.is_owner(request)


@admin.register(Review)
class ReviewAdmin(ControlAdmin):
    list_display          = ('user', 'book', 'stars', 'comment', 'date')
    admin_editable_fields = ('comment',)
    list_filter           = ('stars',)
    search_fields         = ('book__title', 'user__username', 'comment')


    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)