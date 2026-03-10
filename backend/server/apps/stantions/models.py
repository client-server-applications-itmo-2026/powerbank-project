from django.db import models


class StantionTypeModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    max_slots = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class BatteryTypeModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    compatipable_with_stantions = models.ManyToManyField(
        StantionTypeModel,
        related_name="compatipable_batterry_types",
    )


class RegisteredBatteryModel(models.Model):
    battery_type = models.ForeignKey(
        BatteryTypeModel, on_delete=models.PROTECT, related_name="batteries"
    )
    hardware_id = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class RegisteredStantionModel(models.Model):
    stantion_type = models.ForeignKey(
        StantionTypeModel,
        on_delete=models.PROTECT,
        related_name="stantions",
    )
    # TODO: Подключить django.contrib.gis и юзать PointField для хранения координат, а не текстовое поле
    location = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    hardware_id = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class StantionHeartBeatModel(models.Model):

    registered_stantion = models.ForeignKey(
        RegisteredStantionModel,
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now=True)


class SlotStateEnum(models.CharField):
    charged = "charged"
    charging = "charging"
    empty = "empty"


class HeartBeatSlotStateModel(models.Model):
    heartbeat = models.ForeignKey(to=StantionHeartBeatModel, on_delete=models.CASCADE)
    state = models.CharField(choices=SlotStateEnum.choices)
    slot_index = models.PositiveSmallIntegerField()
    registered_battery = models.ForeignKey(
        RegisteredBatteryModel,
        on_delete=models.PROTECT,
    )

    @property
    def state_enum(self) -> SlotStateEnum:
        return SlotStateEnum(self.state)


class StantionTaskModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    to_stantion = models.ForeignKey(
        RegisteredStantionModel,
        on_delete=models.PROTECT,
    )
    task_type = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    # Задача на выдачу АКБ
    payload_release_battery = models.ForeignKey(
        RegisteredBatteryModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    response_release_battery_error = models.TextField(blank=True)
    response_release_battery_success = models.BooleanField(null=True)

    # Задача на прием АКБ
    response_receive_battery_error = models.TextField(blank=True)
    response_receive_battery_success = models.BooleanField(null=True)
    response_release_battery_battery = models.ForeignKey(
        RegisteredBatteryModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expiring_after = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
