from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog, name='blog'),
    path('<str:slug>', views.article_page, name='article_page'),
    path('add_comment/<str:slug>', views.add_comment, name='add_comment'),
]