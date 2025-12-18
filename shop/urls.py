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
    path('cart/checkout/', views.checkout, name='checkout'),
    path('orders/', views.user_order, name='orders'),
    path('orders/<str:order_number>', views.order_detail, name='order-detail'),
    path('orders/change/<str:order_number>', views.order_change, name='order-change'),
    path('cart/checkout/create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('cart/checkout/success/', views.payment_success, name='payment_success'),
    path('cart/checkout/canceled/', views.payment_canceled, name='payment_canceled'),
]