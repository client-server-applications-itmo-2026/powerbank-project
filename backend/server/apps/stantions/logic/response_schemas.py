from typing import Self
from uuid import UUID

from ninja import Schema

from server.apps.stantions.logic.request_schemas import Point
from server.apps.stantions.models import StantionTaskModel, TaskTypeEnum
from server.common.pagination import PaginatedResponse


class RetrieveNearestStantionsResponseItem(Schema):
    hardware_id: str
    location: Point
    free_slots: int
    available_batteries: int


class RetrieveNearestStantionsResponse(
    PaginatedResponse[RetrieveNearestStantionsResponseItem]
): ...


class StantionTaskInfo(Schema):
    task_id: UUID
    task_type: TaskTypeEnum

    # Пока что только она задача, для которой нужно передать payload
    payload_release_battery_hardware_id: str | None = None

    @classmethod
    def from_db_instance(
        cls,
        task_instance: StantionTaskModel,
    ) -> Self:
        return cls(
            task_id=task_instance.id,
            task_type=task_instance.task_type_enum,
            payload_release_battery_hardware_id=task_instance.payload_release_battery_id,  # type: ignore
        )
