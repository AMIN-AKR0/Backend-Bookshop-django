from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login_page, name="login"),
    path('signup/', views.signup_page, name="signup"),
    path('logout/', views.logout_page, name="logout"),
    path('register/', views.register_page, name="register"),
    path('author/<str:slug>', views.author_page, name="author"),
]