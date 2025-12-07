from django.contrib import admin
from blog.models import Comment, Article, BlogCategory, ImageArticle, ArticleView


# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(ImageArticle)
class ImageArticleAdmin(admin.ModelAdmin):
    pass

@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    pass