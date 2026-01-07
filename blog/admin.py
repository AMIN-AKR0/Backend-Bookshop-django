from django.contrib import admin
from .models import Article, ArticleView, ImageArticle, Comment, BlogCategory
from home.admin import ControlAdmin, ControlInlineTabular


class ImageArticleInline(ControlInlineTabular):
    model                 = ImageArticle
    extra                 = 0
    verbose_name          = "Additional Image"
    verbose_name_plural   = "Additional Images"

    admin_editable_fields = ('image',)

    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


class CommentInline(ControlInlineTabular):
    model               = Comment
    extra               = 0
    readonly_fields     = ('user', 'message', 'created')
    can_delete          = True

    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


class ArticleViewInline(ControlInlineTabular):
    model               = ArticleView
    extra               = 0
    readonly_fields     = ('user', 'ip_address', 'token')
    can_delete          = True
    verbose_name        = "View"
    verbose_name_plural = "Views"

    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


@admin.register(Article)
class ArticleAdmin(ControlAdmin):
    list_display          = ('title', 'author', 'category', 'status', 'created',)
    list_filter           = ('status', 'category',)
    search_fields         = ('title', 'author__user__email', 'category__name')
    readonly_fields       = ('slug', 'created', 'author')

    admin_editable_fields = ('status', 'content', 'cover')

    fieldsets       = (
        ("Main Info", {
            'fields': ('title', 'author', 'category', 'status', 'slug')
        }),
        ("Content", {
            'fields': ('content', 'cover')
        }),
    )

    inlines = [ImageArticleInline, CommentInline, ArticleViewInline]

    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


@admin.register(ArticleView)
class ArticleViewAdmin(ControlAdmin):
    list_display    = ('article', 'user', 'ip_address', 'token')
    readonly_fields = ('article', 'user', 'ip_address', 'token')
    search_fields   = ('article__title', 'user__email', 'ip_address', 'token')
    list_filter     = ('article',)

    def has_module_permission(self, request):
        return self.is_owner(request)


@admin.register(Comment)
class CommentAdmin(ControlAdmin):
    list_display          = ('user', 'article', 'short_message', 'created')
    readonly_fields       = ('user', 'article', 'message', 'created')
    search_fields         = ('user__username', 'article__title', 'message')
    list_filter           = ('article', 'user')
    can_delete            = True

    admin_editable_fields = ('message',)

    def short_message(self, obj):
        return obj.message[:50] + ("..." if len(obj.message) > 50 else "")

    short_message.short_description = "Message Preview"

    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


@admin.register(BlogCategory)
class BlogCategoryAdmin(ControlAdmin):
    admin_editable_fields = ('name',)

    fields                = ('name', 'slug',)
    readonly_fields       = ('slug',)

    def has_add_permission(self, request):
        return self.is_admin(request)