import datetime

from ninja import Schema
from pydantic import field_validator

from server.apps.rentals.models import RentalStatusEnum
from server.apps.stantions.logic.request_schemas import Point


class TarrifSchema(Schema):
    id: int
    name: str
    price_per_tick: int | None
    description: str
    is_active: bool

    created_at: datetime.datetime
    update_at: datetime.datetime


class StantionInfoSchema(Schema):
    hardware_id: str
    location: Point

    @field_validator("location", mode="before")
    @classmethod
    def convert_geos_point(cls, value) -> Point:
        return Point.from_geo_point(value)


class RentalSchema(Schema):
    id: int
    user_id: int
    battery_id: str
    tariff: TarrifSchema
    started_at_stantion: StantionInfoSchema
    completed_at_stantion: StantionInfoSchema | None
    final_price: int | None
    status: RentalStatusEnum

    started_at: datetime.datetime
    completed_at: datetime.datetime | None


class TariffSchema(Schema):
    id: int
    name: str
    price_per_tick: int | None
    description: str
    is_active: bool

    created_at: datetime.datetime
    update_at: datetime.datetime
