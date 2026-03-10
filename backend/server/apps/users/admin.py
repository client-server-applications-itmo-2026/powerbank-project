from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from server.apps.users.models import UserModel


@admin.register(UserModel)
class UserModelAdmin(BaseUserAdmin):
    list_display = ("id", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("id",)
    fieldsets = ()
    fields = (
        "email",
        "password",
        "is_staff",
        "is_active",
        "is_stantion_admin",
        "patronymic_name",
        "phone_number",
    )
    exclude = ()
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
