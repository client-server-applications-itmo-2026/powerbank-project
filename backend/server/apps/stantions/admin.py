from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import (
    BatteryTypeModel,
    HeartBeatSlotStateModel,
    RegisteredBatteryModel,
    RegisteredStantionModel,
    StantionHeartBeatModel,
    StantionTaskModel,
    StantionTypeModel,
)


@admin.register(StantionTypeModel)
class StantionTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "max_slots", "created_at", "update_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "update_at")
    fieldsets = (
        (None, {
            "fields": ("name", "max_slots", "description"),
        }),
        ("Временные метки", {
            "fields": ("created_at", "update_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(BatteryTypeModel)
class BatteryTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "update_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "update_at")
    filter_horizontal = ("compatipable_with_stantions",)
    fieldsets = (
        (None, {
            "fields": ("name", "description"),
        }),
        ("Совместимость", {
            "fields": ("compatipable_with_stantions",),
        }),
        ("Временные метки", {
            "fields": ("created_at", "update_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(RegisteredBatteryModel)
class RegisteredBatteryAdmin(admin.ModelAdmin):
    list_display = (
        "hardware_id",
        "battery_type",
        "is_active",
        "is_deleted",
        "created_at",
        "update_at",
    )
    search_fields = ("hardware_id",)
    list_filter = ("is_active", "is_deleted", "battery_type")
    readonly_fields = ("created_at", "update_at")
    autocomplete_fields = ("battery_type",)
    fieldsets = (
        (None, {
            "fields": ("hardware_id", "battery_type"),
        }),
        ("Статус", {
            "fields": ("is_active", "is_deleted"),
        }),
        ("Временные метки", {
            "fields": ("created_at", "update_at"),
            "classes": ("collapse",),
        }),
    )


class HeartBeatSlotStateInline(admin.TabularInline):
    model = HeartBeatSlotStateModel
    extra = 0
    readonly_fields = ("slot_index", "state", "registered_battery")
    can_delete = False


@admin.register(RegisteredStantionModel)
class RegisteredStantionAdmin(GISModelAdmin):
    list_display = (
        "hardware_id",
        "name",
        "stantion_type",
        "is_active",
        "is_deleted",
        "created_at",
        "update_at",
    )
    search_fields = ("hardware_id", "name")
    list_filter = ("is_active", "is_deleted", "stantion_type")
    readonly_fields = ("created_at", "update_at")
    autocomplete_fields = ("stantion_type",)
    fieldsets = (
        (None, {
            "fields": ("hardware_id", "name", "stantion_type"),
        }),
        ("Расположение", {
            "fields": ("location",),
        }),
        ("Статус", {
            "fields": ("is_active", "is_deleted"),
        }),
        ("Временные метки", {
            "fields": ("created_at", "update_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(StantionHeartBeatModel)
class StantionHeartBeatAdmin(admin.ModelAdmin):
    list_display = ("id", "registered_stantion", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
    autocomplete_fields = ("registered_stantion",)
    inlines = [HeartBeatSlotStateInline]


@admin.register(HeartBeatSlotStateModel)
class HeartBeatSlotStateAdmin(admin.ModelAdmin):
    list_display = (
        "heartbeat",
        "state",
        "slot_index",
        "registered_battery",
    )
    list_filter = ("state",)
    search_fields = ("registered_battery__hardware_id",)
    raw_id_fields = ("heartbeat", "registered_battery")


@admin.register(StantionTaskModel)
class StantionTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "to_stantion",
        "task_type",
        "status",
        "created_at",
        "expiring_after",
        "completed_at",
    )
    search_fields = ("id",)
    list_filter = ("task_type", "status")
    readonly_fields = ("id", "created_at", "completed_at")
    autocomplete_fields = ("to_stantion",)
    raw_id_fields = ("payload_release_battery", "response_release_battery_battery")
    date_hierarchy = "created_at"
    fieldsets = (
        ("Задача", {
            "fields": ("id", "to_stantion", "task_type", "status", "expiring_after"),
        }),
        ("Выдача АКБ", {
            "fields": (
                "payload_release_battery",
                "response_release_battery_success",
                "response_release_battery_error",
            ),
            "classes": ("collapse",),
        }),
        ("Приём АКБ", {
            "fields": (
                "response_receive_battery_success",
                "response_receive_battery_error",
                "response_release_battery_battery",
            ),
            "classes": ("collapse",),
        }),
        ("Временные метки", {
            "fields": ("created_at", "completed_at"),
            "classes": ("collapse",),
        }),
    )
