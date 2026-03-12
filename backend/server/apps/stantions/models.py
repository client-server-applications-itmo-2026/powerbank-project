import uuid

from django.contrib.gis.db import models as gis_models
from django.db import models

from server.common.name_generator import generate_name


class StantionTypeModel(models.Model):
    id: int
    name = models.CharField(
        max_length=255,
        unique=True,
        primary_key=True,
    )
    max_slots = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class BatteryTypeModel(models.Model):
    id: int
    name = models.CharField(
        max_length=255,
        unique=True,
        primary_key=True,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    compatipable_with_stantions = models.ManyToManyField(
        StantionTypeModel,
        related_name="compatipable_batterry_types",
    )


class RegisteredBatteryModel(models.Model):
    id: int
    hardware_id = models.CharField(
        max_length=255,
        unique=True,
        primary_key=True,
    )
    battery_type = models.ForeignKey(
        BatteryTypeModel, on_delete=models.PROTECT, related_name="batteries"
    )

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class RegisteredStantionModel(models.Model):
    id: int
    hardware_id = models.CharField(
        max_length=255,
        unique=True,
        primary_key=True,
    )
    stantion_type = models.ForeignKey(
        StantionTypeModel,
        on_delete=models.PROTECT,
        related_name="stantions",
    )
    location = gis_models.PointField(
        spatial_index=True,
        geography=True,
    )

    name = models.CharField(
        max_length=255,
        default=generate_name,
    )

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class StantionHeartBeatModel(models.Model):

    registered_stantion = models.ForeignKey(
        RegisteredStantionModel,
        on_delete=models.PROTECT,
        related_name="heartbeats",
    )
    created_at = models.DateTimeField(auto_now=True)


class SlotStateEnum(models.TextChoices):
    CHARGED = "charged"
    CHARGING = "charging"
    EMPTY = "empty"


class HeartBeatSlotStateModel(models.Model):
    heartbeat = models.ForeignKey(
        to=StantionHeartBeatModel,
        on_delete=models.CASCADE,
        related_name="slot_states",
    )
    state = models.CharField(choices=SlotStateEnum.choices)
    slot_index = models.PositiveSmallIntegerField()
    registered_battery = models.ForeignKey(
        RegisteredBatteryModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    @property
    def state_enum(self) -> SlotStateEnum:
        return SlotStateEnum(self.state)


class TaskStatusEnum(models.TextChoices):
    CREATED = "created"
    RESERVED = "reserved"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


class TaskTypeEnum(models.TextChoices):
    RELEASE_BATTERY = "release_battery"
    RECEIVE_BATTERY = "receive_battery"


class StantionTaskModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
    )
    to_stantion = models.ForeignKey(
        RegisteredStantionModel,
        on_delete=models.PROTECT,
    )
    task_type = models.CharField(
        max_length=255,
        choices=TaskTypeEnum.choices,
    )
    status = models.CharField(
        max_length=255,
        choices=TaskStatusEnum.choices,
        default=TaskStatusEnum.CREATED,
    )

    # Задача на выдачу АКБ
    payload_release_battery = models.ForeignKey(
        RegisteredBatteryModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payload_release_battery_tasks",
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
        related_name="payload_receive_battery_tasks",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expiring_after = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    @property
    def task_type_enum(self) -> TaskTypeEnum:
        return TaskTypeEnum(self.task_type)

    @property
    def status_enum(self) -> TaskStatusEnum:
        return TaskStatusEnum(self.status)
