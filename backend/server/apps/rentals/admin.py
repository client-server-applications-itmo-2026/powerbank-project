from django.contrib import admin

from .models import RentalModel, TariffModel


@admin.register(TariffModel)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "tariff_type", "price_per_tick", "is_active", "created_at")
    list_filter = ("tariff_type", "is_active")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "update_at")
    fieldsets = (
        (None, {
            "fields": ("name", "description"),
        }),
        ("Тарификация", {
            "fields": ("tariff_type", "price_per_tick", "is_active"),
        }),
        ("Временные метки", {
            "fields": ("created_at", "update_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(RentalModel)
class RentalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "battery",
        "tariff",
        "status",
        "final_price",
        "started_at",
        "completed_at",
    )
    list_filter = ("status", "tariff", "started_at")
    search_fields = ("user__email", "battery__hardware_id")
    readonly_fields = ("started_at", "completed_at")
    autocomplete_fields = ("user", "battery", "tariff", "started_at_stantion", "completed_at_stantion")
    raw_id_fields = ("related_release_task", "related_accept_task")
    date_hierarchy = "started_at"
    fieldsets = (
        ("Аренда", {
            "fields": ("user", "battery", "tariff", "status"),
        }),
        ("Станции", {
            "fields": ("started_at_stantion", "completed_at_stantion"),
        }),
        ("Задачи", {
            "fields": ("related_release_task", "related_accept_task"),
            "classes": ("collapse",),
        }),
        ("Оплата", {
            "fields": ("final_price",),
        }),
        ("Временные метки", {
            "fields": ("started_at", "completed_at"),
            "classes": ("collapse",),
        }),
    )

