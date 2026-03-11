import datetime

from django.utils import timezone

from server.apps.stantions.models import (
    RegisteredBatteryModel,
    RegisteredStantionModel,
    SlotStateEnum,
    StantionTaskModel,
    TaskTypeEnum,
)
from server.common.exceptions import DomainError


def create_release_battery_task(
    stantion_instance: RegisteredStantionModel,
    battery_instance: RegisteredBatteryModel | None = None,
) -> StantionTaskModel:
    last_heartbeat = stantion_instance.heartbeats.order_by("-created_at").first()  # type: ignore
    if last_heartbeat is None or (timezone.now() - last_heartbeat.created_at) > datetime.timedelta(minutes=10):
        raise DomainError("Stantion is not active")

    if battery_instance is None:
        battery_instance = last_heartbeat.slot_states.filter(state=SlotStateEnum.CHARGED).first()  # type: ignore
        if battery_instance is None:
            raise DomainError("No charged batteries available at the moment")

    if not last_heartbeat.slot_states.filter(registered_battery=battery_instance).exists():
        raise DomainError("Stantion does not have this battery")

    return StantionTaskModel.objects.create(
        to_stantion=stantion_instance,
        task_type=TaskTypeEnum.RELEASE_BATTERY,
        payload_release_battery=battery_instance,
        expiring_after=timezone.now() + datetime.timedelta(minutes=5),
    )


def create_receive_battery_task(
    stantion_instance: RegisteredStantionModel,
) -> StantionTaskModel:
    return StantionTaskModel.objects.create(
        to_stantion=stantion_instance,
        task_type=TaskTypeEnum.RECEIVE_BATTERY,
        expiring_after=timezone.now() + datetime.timedelta(minutes=5),
    )
