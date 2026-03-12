import base64
import uuid
from datetime import timedelta
from http import HTTPStatus
from typing import final

import pytest
from django.contrib.gis.geos import Point as GeoPoint
from django.test import Client
from django.utils import timezone

from server.apps.stantions.models import (
    BatteryTypeModel,
    RegisteredBatteryModel,
    RegisteredStantionModel,
    StantionTaskModel,
    StantionTypeModel,
    TaskStatusEnum,
    TaskTypeEnum,
)
from server.apps.users.models import UserModel


def _auth_header(email: str, password: str) -> str:
    token = base64.b64encode(f"{email}:{password}".encode()).decode()
    return f"Basic {token}"


@pytest.fixture
def user(db) -> UserModel:
    return UserModel.objects.create_user(
        email="station@example.com",
        password="testpass123",
        first_name="Station",
        last_name="Admin",
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
def created_task(stantion: RegisteredStantionModel) -> StantionTaskModel:
    return StantionTaskModel.objects.create(
        id=uuid.uuid4(),
        to_stantion=stantion,
        task_type=TaskTypeEnum.RELEASE_BATTERY,
        status=TaskStatusEnum.CREATED,
        expiring_after=timezone.now() + timedelta(hours=1),
    )


@pytest.fixture
def reserved_task(stantion: RegisteredStantionModel) -> StantionTaskModel:
    return StantionTaskModel.objects.create(
        id=uuid.uuid4(),
        to_stantion=stantion,
        task_type=TaskTypeEnum.RELEASE_BATTERY,
        status=TaskStatusEnum.RESERVED,
        expiring_after=timezone.now() + timedelta(hours=1),
    )


@pytest.fixture
def accepted_task(stantion: RegisteredStantionModel) -> StantionTaskModel:
    return StantionTaskModel.objects.create(
        id=uuid.uuid4(),
        to_stantion=stantion,
        task_type=TaskTypeEnum.RELEASE_BATTERY,
        status=TaskStatusEnum.ACCEPTED,
        expiring_after=timezone.now() + timedelta(hours=1),
    )


@final
@pytest.mark.django_db
class TestRegisterStantion:
    def test_success(
        self,
        client: Client,
        user: UserModel,
        stantion_type: StantionTypeModel,
    ) -> None:
        response = client.post(
            "/api/register-stantion",
            data={
                "hardware_id": "hw-new",
                "stantion_type_name": "v1",
                "location": {"lat": 55.7558, "lon": 37.6173},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.NO_CONTENT

    def test_requires_auth(self, client: Client, stantion_type: StantionTypeModel) -> None:
        response = client.post(
            "/api/register-stantion",
            data={
                "hardware_id": "hw-new",
                "stantion_type_name": "v1",
                "location": {"lat": 55.7558, "lon": 37.6173},
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


@final
@pytest.mark.django_db
class TestCreateStantionHeartbeat:
    def test_success_for_existing_stantion(
        self,
        client: Client,
        user: UserModel,
        stantion: RegisteredStantionModel,
    ) -> None:
        response = client.post(
            "/api/create-stantion-heartbeat",
            data={
                "stantion_info": {
                    "hardware_id": "hw-001",
                    "model_name": "v1",
                    "location": {"lat": 55.7558, "lon": 37.6173},
                },
                "slot_states": [],
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.NO_CONTENT

    def test_success_creates_stantion_if_not_exists(
        self,
        client: Client,
        user: UserModel,
        stantion_type: StantionTypeModel,
    ) -> None:
        response = client.post(
            "/api/create-stantion-heartbeat",
            data={
                "stantion_info": {
                    "hardware_id": "hw-brand-new",
                    "model_name": "v1",
                    "location": {"lat": 55.7558, "lon": 37.6173},
                },
                "slot_states": [],
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.NO_CONTENT


@final
@pytest.mark.django_db
class TestRetrieveStantions:
    def test_returns_empty_when_no_stantions(
        self, client: Client, user: UserModel
    ) -> None:
        response = client.get(
            "/api/stantions",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["count"] == 0

    def test_returns_active_stantion(
        self,
        client: Client,
        user: UserModel,
        stantion: RegisteredStantionModel,
    ) -> None:
        response = client.get(
            "/api/stantions",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["count"] == 1

    def test_filters_by_location(
        self,
        client: Client,
        user: UserModel,
        stantion: RegisteredStantionModel,
    ) -> None:
        response = client.get(
            "/api/stantions?lat=55.7558&lon=37.6173&radius_meters=500",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["count"] == 1


@final
@pytest.mark.django_db
class TestPullStantionTask:
    def test_success(
        self,
        client: Client,
        user: UserModel,
        created_task: StantionTaskModel,
    ) -> None:
        response = client.post(
            "/api/pull-stantion-task",
            data={"hardware_id": "hw-001"},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK
        assert "task_id" in response.json()

    def test_no_tasks_returns_conflict(
        self, client: Client, user: UserModel, stantion: RegisteredStantionModel
    ) -> None:
        response = client.post(
            "/api/pull-stantion-task",
            data={"hardware_id": "hw-001"},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.CONFLICT


@final
@pytest.mark.django_db
class TestAcceptStantionTask:
    def test_success(
        self,
        client: Client,
        user: UserModel,
        reserved_task: StantionTaskModel,
    ) -> None:
        response = client.post(
            "/api/accept-stantion-task",
            data={"hardware_id": "hw-001", "task_id": str(reserved_task.id)},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK

    def test_non_reserved_task_returns_conflict(
        self,
        client: Client,
        user: UserModel,
        created_task: StantionTaskModel,
    ) -> None:
        response = client.post(
            "/api/accept-stantion-task",
            data={"hardware_id": "hw-001", "task_id": str(created_task.id)},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.CONFLICT


@final
@pytest.mark.django_db
class TestCreateStantionTaskResult:
    def test_success_release_battery(
        self,
        client: Client,
        user: UserModel,
        accepted_task: StantionTaskModel,
    ) -> None:
        response = client.post(
            "/api/create-stantion-task-result",
            data={
                "hardware_id": "hw-001",
                "task_id": str(accepted_task.id),
                "result": {"success": True, "error": None},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK

    def test_non_accepted_task_returns_conflict(
        self,
        client: Client,
        user: UserModel,
        created_task: StantionTaskModel,
    ) -> None:
        response = client.post(
            "/api/create-stantion-task-result",
            data={
                "hardware_id": "hw-001",
                "task_id": str(created_task.id),
                "result": {"success": True, "error": None},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.CONFLICT
