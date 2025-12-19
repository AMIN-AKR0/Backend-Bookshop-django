from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login_page, name="login"),
    path('signup/', views.signup_page, name="signup"),
    path('logout/', views.logout_page, name="logout"),
    path('register/', views.register_page, name="register"),
    path('login/forgot-password/', views.forgot_password_page, name="forgot_password"),
    path('login/forgot-password/validation', views.phone_forgot_password_validation, name="number_validation"),
    path('login/reset-password/<int:number>', views.reset_password_page, name="reset_password_by_number"),
    path('login/reset-password/<str:token>', views.reset_password_page, name="reset_password_by_email"),
    path('author/<str:slug>', views.author_page, name="author"),
    path('author/change/', views.change_author_info, name="author_change"),
    path('profile/', views.profile_page, name="profile"),
    path('profile/add_email/', views.add_email, name="add_email"),
    path('profile/verify_email/<str:token>', views.verify_email, name="verify_email"),
    path('profile/edit/', views.change_profile, name="change_profile"),
    path('profile/change_number/', views.change_number, name="change_number"),
    path('profile/change_password/', views.change_password, name="change_password"),
]