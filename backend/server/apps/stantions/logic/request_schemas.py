from uuid import UUID

from django.contrib.gis.geos import Point as GeoPoint
from ninja import Schema

from server.apps.stantions.models import SlotStateEnum


class Point(Schema):
    lat: float
    lon: float

    def as_geo_point(self) -> GeoPoint:
        return GeoPoint(self.lon, self.lat, srid=4326)


class RegisterStantionRequest(Schema):
    stantion_type_name: str
    location: Point
    hardware_id: str


class BatteryInfo(Schema):
    hardware_id: str
    model_name: str


class StantionInfo(Schema):
    hardware_id: str
    model_name: str
    location: Point


class SlotState(Schema):
    slot_index: int
    # Можно было бы сделать вложенным обеъктом для обозначения пустоты
    # Но чтобы не усложнять, просто сделаем так, что при empty, battery None
    state: SlotStateEnum
    battery_info: BatteryInfo | None


class CreateStantionHeartBeatRequest(Schema):
    stantion_info: StantionInfo
    slot_states: list[SlotState]


class ReleaseBatteryTaskResult(Schema):
    error: str | None = None
    success: bool


class ReceiveBatteryTaskResult(Schema):
    success: bool
    error: str | None = None
    received_battery: BatteryInfo | None = None


class CreateStantionTaskResultRequest(Schema):
    hardware_id: str
    task_id: UUID
    result: ReleaseBatteryTaskResult | ReceiveBatteryTaskResult


class PullStantionTaskRequest(Schema):
    hardware_id: str


class AcceptStantionTaskRequest(Schema):
    hardware_id: str
    task_id: UUID


# Я не уверен что django-ninja умеет нормально работать
# c Union типов, так что просто сделаем один запрос для всех типов задач
# class CreateTaskRequest(Schema):
#     hardware_id: str
#     task_type: TaskTypeEnum
#     payload_battery_hardware_id: str | None = None


class RetrieveNearestStantionsRequest(Schema):
    location: Point | None = None
    radius_meters: int = 2000
    limit: int = 100
    offset: int = 0


class RetrieveNearestStantionsQueryParams(Schema):
    lat: float | None = None
    lon: float | None = None
    radius_meters: int = 2000
    limit: int = 100
    offset: int = 0

    def as_request(self) -> RetrieveNearestStantionsRequest:
        location = None
        if self.lat is not None and self.lon is not None:
            location = Point(lat=self.lat, lon=self.lon)
        return RetrieveNearestStantionsRequest(
            location=location,
            radius_meters=self.radius_meters,
            limit=self.limit,
            offset=self.offset,
        )
