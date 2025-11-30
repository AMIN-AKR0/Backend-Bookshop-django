from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, UserProfile


# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model        = User
    list_display = ("number", "username", "email")
    list_filter  = ("is_active", "is_staff", "is_superuser")
    fieldsets    = (
        (None, {"fields": ("email", "password", "number", "username")}),
        ("Permissions", {"fields": ("is_active", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "username", "password1", "password2",
                "is_active"
            )}
         ),
    )
    search_fields = ("username", "number")
    ordering      = ("email",)


@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    pass