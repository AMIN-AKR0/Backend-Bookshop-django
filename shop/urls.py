from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop, name='shop'),
    path('books/<str:slug>', views.book_detail, name='book-detail'),
    path('books/<str:slug>/add_review', views.add_review, name='add_review'),
    path('cart/', views.cart, name='cart'),
    path('add_cart/', views.add_cart, name='add_cart'),
    path('add_cart/<str:slug>', views.add_cart_one, name='add_cart_one'),
    path('delete_cart/<str:slug>', views.delete_cart, name='delete_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('orders/', views.user_order, name='orders'),
    path('orders/<str:order_number>', views.order_detail, name='order-detail'),
    path('orders/change/<str:order_number>', views.order_change, name='order-change'),
    path('cart/checkout/create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('cart/checkout/success/', views.payment_success, name='payment_success'),
    path('cart/checkout/canceled/', views.payment_canceled, name='payment_canceled'),
    path('author/books/add/', views.add_book, name='add_book'),
    path('shop/author/add_cover/', views.upload_book_cover, name='upload_book_cover'),
    path('author/books/', views.author_books, name='author_books'),
    path('shop/author/books/change/<str:slug>', views.book_change, name='book_change'),
]