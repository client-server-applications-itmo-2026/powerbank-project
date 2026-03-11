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
    list_display = ("name", "max_slots", "description", "created_at", "update_at")
    search_fields = ("name",)
    list_filter = ("created_at", "update_at")


@admin.register(BatteryTypeModel)
class BatteryTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at", "update_at")
    search_fields = ("name",)
    list_filter = ("created_at", "update_at")


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
    list_filter = ("is_active", "is_deleted", "created_at", "update_at")


@admin.register(RegisteredStantionModel)
class RegisteredStantionAdmin(GISModelAdmin):
    list_display = (
        "hardware_id",
        "stantion_type",
        "location",
        "name",
        "is_active",
        "is_deleted",
        "created_at",
        "update_at",
    )
    search_fields = ("hardware_id", "name")
    list_filter = ("is_active", "is_deleted", "created_at", "update_at")


@admin.register(StantionHeartBeatModel)
class StantionHeartBeatAdmin(admin.ModelAdmin):
    list_display = ("registered_stantion", "created_at")
    list_filter = ("created_at",)


@admin.register(HeartBeatSlotStateModel)
class HeartBeatSlotStateAdmin(admin.ModelAdmin):
    list_display = (
        "heartbeat",
        "state",
        "slot_index",
        "registered_battery",
    )
    list_filter = ("state",)


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
    list_filter = ("task_type", "status", "created_at", "expiring_after")
