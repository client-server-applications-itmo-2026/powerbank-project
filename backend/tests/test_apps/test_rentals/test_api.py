import base64
from http import HTTPStatus
from typing import final

import pytest
from django.contrib.gis.geos import Point as GeoPoint
from django.test import Client

from server.apps.rentals.models import (
    RentalModel,
    RentalStatusEnum,
    TariffModel,
    TarrifTypeEnum,
)
from server.apps.stantions.models import (
    BatteryTypeModel,
    HeartBeatSlotStateModel,
    RegisteredBatteryModel,
    RegisteredStantionModel,
    SlotStateEnum,
    StantionHeartBeatModel,
    StantionTypeModel,
)
from server.apps.users.models import UserModel


def _auth_header(email: str, password: str) -> str:
    token = base64.b64encode(f"{email}:{password}".encode()).decode()
    return f"Basic {token}"


@pytest.fixture
def user(db) -> UserModel:
    return UserModel.objects.create_user(
        email="renter@example.com",
        password="testpass123",
        first_name="Renter",
        last_name="User",
    )


@pytest.fixture
def stantion_type(db) -> StantionTypeModel:
    return StantionTypeModel.objects.create(name="v1", max_slots=4)


@pytest.fixture
def battery_type(db) -> BatteryTypeModel:
    return BatteryTypeModel.objects.create(name="bat-v1")


@pytest.fixture
def stantion(stantion_type: StantionTypeModel) -> RegisteredStantionModel:
    return RegisteredStantionModel.objects.create(
        hardware_id="hw-001",
        stantion_type=stantion_type,
        location=GeoPoint(37.6173, 55.7558, srid=4326),
        name="Test Station",
    )


@pytest.fixture
def battery(battery_type: BatteryTypeModel) -> RegisteredBatteryModel:
    return RegisteredBatteryModel.objects.create(
        hardware_id="bat-001",
        battery_type=battery_type,
    )


@pytest.fixture
def tariff(db) -> TariffModel:
    return TariffModel.objects.create(
        name="Basic",
        price_per_tick=100,
        tariff_type=TarrifTypeEnum.FIXED,
    )


@pytest.fixture
def stantion_with_charged_battery(
    stantion: RegisteredStantionModel,
    battery: RegisteredBatteryModel,
) -> RegisteredStantionModel:
    heartbeat = StantionHeartBeatModel.objects.create(registered_stantion=stantion)
    HeartBeatSlotStateModel.objects.create(
        heartbeat=heartbeat,
        state=SlotStateEnum.CHARGED,
        slot_index=0,
        registered_battery=battery,
    )
    return stantion


@pytest.fixture
def active_rental(
    user: UserModel,
    stantion: RegisteredStantionModel,
    battery: RegisteredBatteryModel,
    tariff: TariffModel,
) -> RentalModel:
    return RentalModel.objects.create(
        user=user,
        battery=battery,
        tariff=tariff,
        started_at_stantion=stantion,
        status=RentalStatusEnum.ACTIVE,
    )


@final
@pytest.mark.django_db
class TestRetrieveMyRentals:
    def test_returns_empty_list(self, client: Client, user: UserModel) -> None:
        response = client.get(
            "/api/me/rentals",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == []

    def test_returns_user_rentals(
        self, client: Client, user: UserModel, active_rental: RentalModel
    ) -> None:
        response = client.get(
            "/api/me/rentals",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()["items"]) == 1

    def test_requires_auth(self, client: Client) -> None:
        response = client.get("/api/me/rentals")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

   


@final
@pytest.mark.django_db
class TestStartRental:
    def test_success(
        self,
        client: Client,
        user: UserModel,
        stantion_with_charged_battery: RegisteredStantionModel,
        tariff: TariffModel,
    ) -> None:
        response = client.post(
            "/api/start-rental",
            data={"stantion_id": "hw-001", "tariff_id": tariff.id},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK

    def test_stantion_without_heartbeat_returns_conflict(
        self,
        client: Client,
        user: UserModel,
        stantion: RegisteredStantionModel,
        tariff: TariffModel,
    ) -> None:
        response = client.post(
            "/api/start-rental",
            data={"stantion_id": "hw-001", "tariff_id": tariff.id},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.CONFLICT

    def test_requires_auth(self, client: Client) -> None:
        response = client.post(
            "/api/start-rental",
            data={"stantion_id": "hw-001", "tariff_id": 1},
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        
    def test_user_cannot_start_second_rental(
        self,
        client: Client,
        user: UserModel,
        stantion_with_charged_battery: RegisteredStantionModel,
        tariff: TariffModel,
    ) -> None:
        client.post(
            "/api/start-rental",
            data={
                "stantion_id": stantion_with_charged_battery.hardware_id,
                "tariff_id": tariff.id,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
    
        response = client.post(
            "/api/start-rental",
            data={
                "stantion_id": stantion_with_charged_battery.hardware_id,
                "tariff_id": tariff.id,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )

        assert response.status_code in (HTTPStatus.CONFLICT, HTTPStatus.BAD_REQUEST)

    def test_user_cannot_complete_rental_of_another_user(
        self,
        client: Client,
        active_rental: RentalModel,
        stantion: RegisteredStantionModel,
    ) -> None:
        other_user = UserModel.objects.create_user(
            email="other@example.com",
            password="pass123",
        )
    
        response = client.post(
            "/api/complete-rental",
            data={
                "rental_id": active_rental.id,
                "stantion_id": stantion.hardware_id,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(other_user.email, "pass123"),
        )
    
        assert response.status_code in (
            HTTPStatus.NOT_FOUND,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.CONFLICT,
        )

    def test_response_contains_rental_id(
        self,
        client: Client,
        user: UserModel,
        stantion_with_charged_battery: RegisteredStantionModel,
        tariff: TariffModel,
    ) -> None:
        response = client.post(
            "/api/start-rental",
            data={"stantion_id": "hw-001", "tariff_id": tariff.id},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
    
        assert response.status_code == HTTPStatus.OK
        assert "id" in response.json()


@final
@pytest.mark.django_db
class TestCompleteRental:
    def test_non_active_rental_returns_conflict(
        self,
        client: Client,
        user: UserModel,
        active_rental: RentalModel,
        stantion: RegisteredStantionModel,
    ) -> None:
        active_rental.status = RentalStatusEnum.COMPLETED
        active_rental.save()
        response = client.post(
            "/api/complete-rental",
            data={"rental_id": active_rental.id, "stantion_id": "hw-001"},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.CONFLICT
    def test_user_cannot_complete_rental_of_another_user(
        self,
        client: Client,
        active_rental: RentalModel,
        stantion: RegisteredStantionModel,
    ) -> None:
        other_user = UserModel.objects.create_user(
            email="other@example.com",
            password="pass",
        )

        response = client.post(
            "/api/complete-rental",
            data={
                "rental_id": active_rental.id,
                "stantion_id": stantion.hardware_id,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(other_user.email, "pass"),
        )

        assert response.status_code in (
            HTTPStatus.NOT_FOUND,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.CONFLICT,
        )
