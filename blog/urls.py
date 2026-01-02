from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog, name='blog'),
    path('articles/<str:slug>', views.article_page, name='article_page'),
    path('articles/add_comment/<str:slug>', views.add_comment, name='add_comment'),
    path('articles/author/add/', views.add_article, name='add_article'),
    path('articles/author/upload_cover/', views.upload_cover, name='upload_cover'),
    path('articles/author/upload_image/', views.upload_image, name='upload_image'),
    path('articles/author/delete_image/', views.delete_image, name='delete_image'),
    path('author/articles/', views.author_articles, name='author_articles'),
    path('articles/author/delete/<str:slug>', views.delete_author_articles, name='delete_article'),
    ]