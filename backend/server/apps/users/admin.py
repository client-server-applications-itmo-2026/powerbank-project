from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from server.apps.users.models import UserModel


@admin.register(UserModel)
class UserModelAdmin(BaseUserAdmin):
    list_display = ("id", "email", "first_name", "last_name", "is_staff", "is_stantion_admin", "is_active")
    list_filter = ("is_staff", "is_active", "is_stantion_admin")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("-id",)
    readonly_fields = ("last_login", "date_joined", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("email", "password"),
        }),
        ("Личные данные", {
            "fields": ("first_name", "last_name", "patronymic_name", "phone_number"),
        }),
        ("Права доступа", {
            "fields": ("is_active", "is_staff", "is_superuser", "is_stantion_admin", "groups", "user_permissions"),
        }),
        ("Временные метки", {
            "fields": ("last_login", "date_joined", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_stantion_admin"),
        }),
    )
