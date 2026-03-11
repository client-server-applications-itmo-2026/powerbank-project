from collections import Counter
from typing import Any

from django.contrib.gis.measure import Distance
from django.db import transaction
from django.db.models import F, Prefetch, Window
from django.db.models import functions as db_functions
from structlog import getLogger

from server.apps.rentals.logic import public as rentals_public_logic
from server.apps.stantions.logic.request_schemas import (
    AcceptStantionTaskRequest,
    CreateStantionHeartBeatRequest,
    CreateStantionTaskResultRequest,
    Point,
    PullStantionTaskRequest,
    ReceiveBatteryTaskResult,
    RegisterStantionRequest,
    ReleaseBatteryTaskResult,
    RetrieveNearestStantionsRequest,
)
from server.apps.stantions.logic.response_schemas import (
    RetrieveNearestStantionsResponse,
    RetrieveNearestStantionsResponseItem,
)
from server.apps.stantions.models import (
    HeartBeatSlotStateModel,
    RegisteredBatteryModel,
    RegisteredStantionModel,
    SlotStateEnum,
    StantionHeartBeatModel,
    StantionTaskModel,
    TaskStatusEnum,
)
from server.common.exceptions import DomainError

logger = getLogger(__name__)


@transaction.atomic
def create_stantion_hearbeat(
    data: CreateStantionHeartBeatRequest,
) -> StantionHeartBeatModel:

    # Каюсь, грешил. Но бля... С каким удовольствием
    # я бы с радостью сделал по-людски, но не за 3 дня ;)
    stantion_instance, _ = RegisteredStantionModel.objects.get_or_create(
        hardware_id=data.stantion_info.hardware_id,
        defaults={
            "name": data.stantion_info.hardware_id,
            "location": data.stantion_info.location.as_geo_point(),
            "stantion_type_id": data.stantion_info.model_name,
        },
    )

    received_batteries_hw_ids = {
        slot_state.battery_info.hardware_id
        for slot_state in data.slot_states
        if slot_state.battery_info is not None
    }
    exising_batteries_hw_ids = set(
        RegisteredBatteryModel.objects.filter(
            hardware_id__in=received_batteries_hw_ids,
        ).values_list("hardware_id", flat=True)
    )

    missing_batteries_hw_ids = received_batteries_hw_ids - exising_batteries_hw_ids
    missing_batteries_instances = [
        RegisteredBatteryModel(
            hardware_id=slot_state.battery_info.hardware_id,
            battery_type_id=slot_state.battery_info.model_name,
        )
        for slot_state in data.slot_states
        if slot_state.battery_info is not None
        and slot_state.battery_info.hardware_id in missing_batteries_hw_ids
    ]
    missing_batteries_instances = RegisteredBatteryModel.objects.bulk_create(
        missing_batteries_instances,
        ignore_conflicts=True,
    )

    heartbeat_instance = StantionHeartBeatModel.objects.create(
        registered_stantion=stantion_instance,
    )
    batteries_by_hw_id = {
        battery.hardware_id: battery
        for battery in RegisteredBatteryModel.objects.filter(
            hardware_id__in=received_batteries_hw_ids,
        )
    }

    heartbeat_slot_instances = []
    for slot_state in data.slot_states:
        battery_instance = None

        if slot_state.battery_info is not None:
            battery_instance = batteries_by_hw_id[slot_state.battery_info.hardware_id]

        battery_instance = (
            batteries_by_hw_id.get(slot_state.battery_info.hardware_id)
            if slot_state.battery_info is not None
            else None
        )
        heartbeat_slot_instances.append(
            HeartBeatSlotStateModel(
                heartbeat=heartbeat_instance,
                state=slot_state.state,
                slot_index=slot_state.slot_index,
                registered_battery=battery_instance,
            )
        )
    HeartBeatSlotStateModel.objects.bulk_create(heartbeat_slot_instances)

    return heartbeat_instance


def register_stantion(data: RegisterStantionRequest) -> RegisteredStantionModel:
    return RegisteredStantionModel.objects.create(
        hardware_id=data.hardware_id,
        name=data.hardware_id,
        location=data.location.as_geo_point(),
        stantion_type_id=data.stantion_type_name,
    )


def create_task(data: Any):
    """Пока что просто заглушка. Использовать админку."""
    raise DomainError("Not implemented")


def get_nearest_stantions(
    data: RetrieveNearestStantionsRequest,
) -> RetrieveNearestStantionsResponse:

    registered_stantions_qs = RegisteredStantionModel.objects.filter(
        is_active=True,
        is_deleted=False,
    )

    if data.location is not None:
        user_location_point = data.location.as_geo_point()
        registered_stantions_qs = registered_stantions_qs.filter(
            location__distance_lte=(
                user_location_point,
                Distance(m=data.radius_meters),
            ),
        )

    paginated_qs = registered_stantions_qs[data.offset : data.offset + data.limit]
    latest_heartbeat_qs = (
        StantionHeartBeatModel.objects.annotate(
            rn=Window(
                expression=db_functions.RowNumber(),
                partition_by=[F("registered_stantion_id")],
                order_by=[F("created_at").desc(), F("id").desc()],
            )
        )
        .filter(rn=1)
        .prefetch_related("slot_states")
    )
    paginated_qs = paginated_qs.select_related("stantion_type").prefetch_related(
        Prefetch(
            "heartbeats",
            queryset=latest_heartbeat_qs,
            to_attr="latest_heartbeat",
        )
    )
    response_items = []
    for stantion in paginated_qs:
        latest_heartbeat: StantionHeartBeatModel | None = (
            stantion.latest_heartbeat[0] if stantion.latest_heartbeat else None  # type: ignore
        )
        free_slots = 0
        available_batteries = 0
        if latest_heartbeat is not None:
            states_values = [
                slot_state.state_enum
                for slot_state in latest_heartbeat.slot_states.all()
            ]
            states_counter = Counter(states_values)
            free_slots = states_counter[SlotStateEnum.EMPTY]
            available_batteries = states_counter[SlotStateEnum.CHARGED]

        response_items.append(
            RetrieveNearestStantionsResponseItem(
                hardware_id=stantion.hardware_id,
                location=Point(
                    lat=stantion.location.y,
                    lon=stantion.location.x,
                ),
                free_slots=free_slots,
                available_batteries=available_batteries,
            )
        )
    return RetrieveNearestStantionsResponse(
        count=registered_stantions_qs.count(),
        results=response_items,
    )


@transaction.atomic
def pull_stantion_task(data: PullStantionTaskRequest) -> StantionTaskModel:
    task_qs = (
        StantionTaskModel.objects.filter(
            to_stantion_id=data.hardware_id, status=TaskStatusEnum.CREATED
        )
        .order_by("-created_at")
        .select_for_update(skip_locked=True)
    )

    task_instance = task_qs.first()
    if task_instance is None:
        raise DomainError("No tasks available")

    task_instance.status = TaskStatusEnum.RESERVED
    task_instance.save(update_fields=["status"])
    return task_instance


@transaction.atomic
def accept_stantion_task(data: AcceptStantionTaskRequest) -> StantionTaskModel:
    task_qs = StantionTaskModel.objects.filter(
        id=data.task_id,
        to_stantion_id=data.hardware_id,
        status=TaskStatusEnum.RESERVED,
    ).select_for_update()

    task_instance = task_qs.first()
    if task_instance is None:
        raise DomainError("Task not found or not in RESERVED status")

    task_instance.status = TaskStatusEnum.ACCEPTED
    task_instance.save(update_fields=["status"])
    return task_instance


def complete_stantion_task(data: CreateStantionTaskResultRequest) -> StantionTaskModel:
    with transaction.atomic():
        task_qs = StantionTaskModel.objects.filter(
            id=data.task_id,
            to_stantion_id=data.hardware_id,
            status=TaskStatusEnum.ACCEPTED,
        ).select_for_update()

        task_instance = task_qs.first()
        if task_instance is None:
            raise DomainError("Task not found or not in ACCEPTED status")

        # Тут можно было бы по-хорошему еще проверять, что результат соответствует типу задачи
        task_instance.status = TaskStatusEnum.COMPLETED

        # А тут придумать велосипед для более элегантного сохранения результата
        # Но мне за это не платят, так что пох+пох
        if isinstance(data.result, ReleaseBatteryTaskResult):
            task_instance.response_release_battery_success = data.result.success
            task_instance.response_release_battery_error = data.result.error or ""
        elif isinstance(data.result, ReceiveBatteryTaskResult):
            task_instance.response_receive_battery_success = data.result.success
            task_instance.response_receive_battery_error = data.result.error or ""

            if data.result.received_battery is not None:
                battery_instance, _ = RegisteredBatteryModel.objects.get_or_create(
                    hardware_id=data.result.received_battery.hardware_id,
                    defaults={
                        "battery_type_id": data.result.received_battery.model_name,
                    },
                )
                task_instance.response_release_battery_battery = battery_instance

        if not any(
            [
                task_instance.response_release_battery_success,
                task_instance.response_receive_battery_success,
            ]
        ):
            task_instance.status = TaskStatusEnum.FAILED

        task_instance.save()

    # Подписчик-продюсер для бедных
    try:
        rentals_public_logic.handle_complete_success_task(task_instance)
    except Exception as e:
        logger.exception("Error during notifying rental about task completion: %s", e)
    return task_instance
