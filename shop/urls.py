from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop, name='shop'),
    path('books/<str:slug>', views.book_detail, name='book-detail'),
    path('books/<str:slug>/add_review', views.add_review, name='add_review'),
    path('cart/', views.cart, name='cart'),
    path('add_cart/', views.add_cart, name='add_cart'),
    path('delete_cart/<str:slug>', views.delete_cart, name='delete_cart'),
]