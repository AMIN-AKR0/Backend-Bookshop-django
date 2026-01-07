from django.contrib import admin
from .models import SiteSettings

# Register your models here.
class ControlAdmin(admin.ModelAdmin):
    admin_editable_fields = ()

    def is_owner(self, request):
        return request.user.is_superuser and request.user.is_staff

    def is_admin(self, request):
        return request.user.is_staff or request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        if self.is_owner(request):
            return super().get_readonly_fields(request, obj)

        all_fields = [f.name for f in self.model._meta.fields]

        return [f for f in all_fields if f not in self.admin_editable_fields]

    def has_add_permission(self, request):
        return self.is_owner(request)

    def has_delete_permission(self, request, obj=None):
        return self.is_owner(request)

    def has_view_permission(self, request, obj=None):
        return self.is_admin(request)

    def has_change_permission(self, request, obj=None):
        return self.is_admin(request)

    def has_module_permission(self, request):
        return self.is_admin(request)


class ControlInlineTabular(admin.TabularInline):
    can_delete            = False
    extra                 = 0

    admin_editable_fields = ()

    def is_owner(self, request):
        return request.user.is_superuser and request.user.is_staff

    def is_admin(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return self.is_owner(request)

    def has_delete_permission(self, request, obj=None):
        return self.is_owner(request)

    def get_readonly_fields(self, request, obj=None):
        if self.is_owner(request):
            return super().get_readonly_fields(request, obj)

        all_fields = [f.name for f in self.model._meta.fields]

        return [f for f in all_fields if f not in self.admin_editable_fields]

    def has_module_permission(self, request):
        return self.is_admin(request)

    def has_view_permission(self, request, obj=None):
        return self.is_admin(request)

    def has_change_permission(self, request, obj=None):
        return self.is_admin(request)


class ControlInlineStacked(admin.StackedInline):
    extra                 = 0
    can_delete            = False
    show_change_link      = False

    admin_editable_fields = ()

    def is_owner(self, request):
        return request.user.is_superuser and request.user.is_staff

    def is_admin(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return self.is_owner(request)

    def has_delete_permission(self, request, obj=None):
        return self.is_owner(request)

    def has_change_permission(self, request, obj=None):
        return self.is_admin(request)

    def get_readonly_fields(self, request, obj=None):
        if self.is_owner(request):
            return super().get_readonly_fields(request, obj)

        all_fields = [f.name for f in self.model._meta.fields]

        return [f for f in all_fields if f not in self.admin_editable_fields]

    def has_module_permission(self, request):
        return self.is_admin(request)

    def has_view_permission(self, request, obj=None):
        return self.is_admin(request)


@admin.register(SiteSettings)
class SiteSettingsAdmin(ControlAdmin):
    def has_module_permission(self, request):
        return self.is_owner(request)

    def has_add_permission(self, request):
        if SiteSettings.objects.count() < 1:
            return self.is_owner(request)

        return False