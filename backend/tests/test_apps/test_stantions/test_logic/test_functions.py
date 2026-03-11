import uuid
from datetime import timedelta
from typing import final

import pytest
from django.contrib.gis.geos import Point as GeoPoint
from django.utils import timezone

from server.apps.stantions.logic.functions import (
    accept_stantion_task,
    complete_stantion_task,
    create_stantion_hearbeat,
    create_task,
    get_nearest_stantions,
    pull_stantion_task,
    register_stantion,
)
from server.apps.stantions.logic.request_schemas import (
    AcceptStantionTaskRequest,
    BatteryInfo,
    CreateStantionHeartBeatRequest,
    CreateStantionTaskResultRequest,
    Point,
    PullStantionTaskRequest,
    ReceiveBatteryTaskResult,
    RegisterStantionRequest,
    ReleaseBatteryTaskResult,
    RetrieveNearestStantionsRequest,
    SlotState,
    StantionInfo,
)
from server.apps.stantions.models import (
    BatteryTypeModel,
    HeartBeatSlotStateModel,
    RegisteredBatteryModel,
    RegisteredStantionModel,
    SlotStateEnum,
    StantionHeartBeatModel,
    StantionTaskModel,
    StantionTypeModel,
    TaskStatusEnum,
    TaskTypeEnum,
)
from server.common.exceptions import DomainError

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_MOSCOW_LON = 37.6173
_MOSCOW_LAT = 55.7558
_SPB_LON = 30.3351
_SPB_LAT = 59.9343


def _moscow_geo_point() -> GeoPoint:
    return GeoPoint(_MOSCOW_LON, _MOSCOW_LAT, srid=4326)


def _moscow_point() -> Point:
    return Point(lat=_MOSCOW_LAT, lon=_MOSCOW_LON)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def stantion_type(db) -> StantionTypeModel:
    return StantionTypeModel.objects.create(name="v1", max_slots=4)


@pytest.fixture
def battery_type(db) -> BatteryTypeModel:
    return BatteryTypeModel.objects.create(name="bat-v1")


@pytest.fixture
def stantion(stantion_type) -> RegisteredStantionModel:
    return RegisteredStantionModel.objects.create(
        hardware_id="hw-001",
        stantion_type=stantion_type,
        location=_moscow_geo_point(),
        name="Test Stantion",
    )


@pytest.fixture
def battery(battery_type) -> RegisteredBatteryModel:
    return RegisteredBatteryModel.objects.create(
        hardware_id="bat-001",
        battery_type=battery_type,
    )


@pytest.fixture
def created_task(stantion) -> StantionTaskModel:
    return StantionTaskModel.objects.create(
        id=uuid.uuid4(),
        to_stantion=stantion,
        task_type=TaskTypeEnum.RELEASE_BATTERY,
        status=TaskStatusEnum.CREATED,
        expiring_after=timezone.now() + timedelta(hours=1),
    )


@pytest.fixture
def reserved_task(stantion) -> StantionTaskModel:
    return StantionTaskModel.objects.create(
        id=uuid.uuid4(),
        to_stantion=stantion,
        task_type=TaskTypeEnum.RELEASE_BATTERY,
        status=TaskStatusEnum.RESERVED,
        expiring_after=timezone.now() + timedelta(hours=1),
    )


@pytest.fixture
def accepted_task(stantion) -> StantionTaskModel:
    return StantionTaskModel.objects.create(
        id=uuid.uuid4(),
        to_stantion=stantion,
        task_type=TaskTypeEnum.RECEIVE_BATTERY,
        status=TaskStatusEnum.ACCEPTED,
        expiring_after=timezone.now() + timedelta(hours=1),
    )


# ---------------------------------------------------------------------------
# Tests: create_task (stub)
# ---------------------------------------------------------------------------


@final
class TestCreateTask:
    """create_task is a not-implemented stub."""

    def test_raises_domain_error(self) -> None:
        with pytest.raises(DomainError, match="Not implemented"):
            create_task(None)


# ---------------------------------------------------------------------------
# Tests: register_stantion
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestRegisterStantion:
    def test_creates_stantion_in_db(self, stantion_type: StantionTypeModel) -> None:
        data = RegisterStantionRequest(
            hardware_id="hw-reg",
            stantion_type_name="v1",
            location=_moscow_point(),
        )

        result = register_stantion(data)

        assert result.hardware_id == "hw-reg"
        assert RegisteredStantionModel.objects.filter(hardware_id="hw-reg").exists()


# ---------------------------------------------------------------------------
# Tests: create_stantion_hearbeat
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestCreateStantionHeartbeat:
    def test_creates_heartbeat_for_existing_stantion(
        self, stantion: RegisteredStantionModel
    ) -> None:
        data = CreateStantionHeartBeatRequest(
            stantion_info=StantionInfo(
                hardware_id="hw-001",
                model_name="v1",
                location=_moscow_point(),
            ),
            slot_states=[],
        )

        result = create_stantion_hearbeat(data)

        assert isinstance(result, StantionHeartBeatModel)
        assert result.registered_stantion_id == "hw-001" # type: ignore

    def test_creates_stantion_when_not_exists(
        self, stantion_type: StantionTypeModel
    ) -> None:
        data = CreateStantionHeartBeatRequest(
            stantion_info=StantionInfo(
                hardware_id="hw-new",
                model_name="v1",
                location=_moscow_point(),
            ),
            slot_states=[],
        )

        create_stantion_hearbeat(data)

        assert RegisteredStantionModel.objects.filter(hardware_id="hw-new").exists()

    def test_creates_slot_state_with_new_battery(
        self, stantion: RegisteredStantionModel, battery_type: BatteryTypeModel
    ) -> None:
        data = CreateStantionHeartBeatRequest(
            stantion_info=StantionInfo(
                hardware_id="hw-001",
                model_name="v1",
                location=_moscow_point(),
            ),
            slot_states=[
                SlotState(
                    slot_index=0,
                    state=SlotStateEnum.CHARGED,
                    battery_info=BatteryInfo(
                        hardware_id="bat-new", model_name="bat-v1"
                    ),
                ),
            ],
        )

        result = create_stantion_hearbeat(data)

        assert HeartBeatSlotStateModel.objects.filter(heartbeat=result).count() == 1
        assert RegisteredBatteryModel.objects.filter(hardware_id="bat-new").exists()

    def test_creates_slot_state_with_existing_battery(
        self,
        stantion: RegisteredStantionModel,
        battery: RegisteredBatteryModel,
    ) -> None:
        data = CreateStantionHeartBeatRequest(
            stantion_info=StantionInfo(
                hardware_id="hw-001",
                model_name="v1",
                location=_moscow_point(),
            ),
            slot_states=[
                SlotState(
                    slot_index=0,
                    state=SlotStateEnum.CHARGED,
                    battery_info=BatteryInfo(
                        hardware_id="bat-001", model_name="bat-v1"
                    ),
                ),
            ],
        )

        result = create_stantion_hearbeat(data)

        slot = HeartBeatSlotStateModel.objects.get(heartbeat=result)
        assert slot.registered_battery_id == "bat-001" # type: ignore

    def test_creates_empty_slot_state(
        self, stantion: RegisteredStantionModel
    ) -> None:
        data = CreateStantionHeartBeatRequest(
            stantion_info=StantionInfo(
                hardware_id="hw-001",
                model_name="v1",
                location=_moscow_point(),
            ),
            slot_states=[
                SlotState(
                    slot_index=0,
                    state=SlotStateEnum.EMPTY,
                    battery_info=None,
                ),
            ],
        )

        result = create_stantion_hearbeat(data)

        slot = HeartBeatSlotStateModel.objects.get(heartbeat=result)
        assert slot.state_enum == SlotStateEnum.EMPTY
        assert slot.registered_battery is None

    def test_creates_multiple_slot_states(
        self, stantion: RegisteredStantionModel, battery_type: BatteryTypeModel
    ) -> None:
        data = CreateStantionHeartBeatRequest(
            stantion_info=StantionInfo(
                hardware_id="hw-001",
                model_name="v1",
                location=_moscow_point(),
            ),
            slot_states=[
                SlotState(
                    slot_index=0,
                    state=SlotStateEnum.CHARGED,
                    battery_info=BatteryInfo(
                        hardware_id="bat-a", model_name="bat-v1"
                    ),
                ),
                SlotState(
                    slot_index=1,
                    state=SlotStateEnum.EMPTY,
                    battery_info=None,
                ),
            ],
        )

        result = create_stantion_hearbeat(data)

        assert HeartBeatSlotStateModel.objects.filter(heartbeat=result).count() == 2


# ---------------------------------------------------------------------------
# Tests: get_nearest_stantions
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestGetNearestStantions:
    def test_returns_active_stantion(
        self, stantion: RegisteredStantionModel
    ) -> None:
        result = get_nearest_stantions(RetrieveNearestStantionsRequest())

        assert result.count == 1
        assert result.results[0].hardware_id == "hw-001"

    def test_excludes_inactive_stantion(
        self, stantion: RegisteredStantionModel
    ) -> None:
        stantion.is_active = False
        stantion.save()

        result = get_nearest_stantions(RetrieveNearestStantionsRequest())

        assert result.count == 0

    def test_excludes_deleted_stantion(
        self, stantion: RegisteredStantionModel
    ) -> None:
        stantion.is_deleted = True
        stantion.save()

        result = get_nearest_stantions(RetrieveNearestStantionsRequest())

        assert result.count == 0

    def test_filters_stantion_within_radius(
        self, stantion: RegisteredStantionModel
    ) -> None:
        data = RetrieveNearestStantionsRequest(
            location=_moscow_point(),
            radius_meters=1000,
        )

        result = get_nearest_stantions(data)

        assert result.count == 1

    def test_excludes_stantion_outside_radius(
        self, stantion: RegisteredStantionModel
    ) -> None:
        data = RetrieveNearestStantionsRequest(
            location=Point(lat=_SPB_LAT, lon=_SPB_LON),
            radius_meters=1000,
        )

        result = get_nearest_stantions(data)

        assert result.count == 0

    def test_stantion_without_heartbeat_returns_zero_slots(
        self, stantion: RegisteredStantionModel
    ) -> None:
        result = get_nearest_stantions(RetrieveNearestStantionsRequest())

        assert result.results[0].free_slots == 0
        assert result.results[0].available_batteries == 0

    def test_counts_free_slots_and_batteries_from_latest_heartbeat(
        self,
        stantion: RegisteredStantionModel,
        battery: RegisteredBatteryModel,
    ) -> None:
        heartbeat = StantionHeartBeatModel.objects.create(
            registered_stantion=stantion
        )
        HeartBeatSlotStateModel.objects.create(
            heartbeat=heartbeat,
            state=SlotStateEnum.EMPTY,
            slot_index=0,
        )
        HeartBeatSlotStateModel.objects.create(
            heartbeat=heartbeat,
            state=SlotStateEnum.CHARGED,
            slot_index=1,
            registered_battery=battery,
        )
        HeartBeatSlotStateModel.objects.create(
            heartbeat=heartbeat,
            state=SlotStateEnum.CHARGING,
            slot_index=2,
            registered_battery=battery,
        )

        result = get_nearest_stantions(RetrieveNearestStantionsRequest())

        assert result.results[0].free_slots == 1
        assert result.results[0].available_batteries == 1

    def test_uses_only_latest_heartbeat(
        self,
        stantion: RegisteredStantionModel,
        battery: RegisteredBatteryModel,
    ) -> None:
        old_heartbeat = StantionHeartBeatModel.objects.create(
            registered_stantion=stantion
        )
        HeartBeatSlotStateModel.objects.create(
            heartbeat=old_heartbeat,
            state=SlotStateEnum.CHARGED,
            slot_index=0,
            registered_battery=battery,
        )
        new_heartbeat = StantionHeartBeatModel.objects.create(
            registered_stantion=stantion
        )
        HeartBeatSlotStateModel.objects.create(
            heartbeat=new_heartbeat,
            state=SlotStateEnum.EMPTY,
            slot_index=0,
        )

        result = get_nearest_stantions(RetrieveNearestStantionsRequest())

        assert result.results[0].free_slots == 1
        assert result.results[0].available_batteries == 0

    def test_pagination_respects_limit_and_offset(
        self, stantion_type: StantionTypeModel
    ) -> None:
        for i in range(3):
            RegisteredStantionModel.objects.create(
                hardware_id=f"hw-{i:03}",
                stantion_type=stantion_type,
                location=GeoPoint(_MOSCOW_LON + i * 0.01, _MOSCOW_LAT, srid=4326),
                name=f"Stantion {i}",
            )

        result = get_nearest_stantions(
            RetrieveNearestStantionsRequest(limit=2, offset=1)
        )

        assert result.count == 3
        assert len(result.results) == 2


# ---------------------------------------------------------------------------
# Tests: pull_stantion_task
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestPullStantionTask:
    def test_returns_created_task_and_sets_reserved(
        self, created_task: StantionTaskModel
    ) -> None:
        data = PullStantionTaskRequest(hardware_id="hw-001")

        result = pull_stantion_task(data)

        assert result.id == created_task.id
        result.refresh_from_db()
        assert result.status_enum == TaskStatusEnum.RESERVED

    def test_raises_when_no_tasks(
        self, stantion: RegisteredStantionModel
    ) -> None:
        with pytest.raises(DomainError, match="No tasks available"):
            pull_stantion_task(PullStantionTaskRequest(hardware_id="hw-001"))

    def test_raises_when_no_created_tasks(
        self, reserved_task: StantionTaskModel
    ) -> None:
        with pytest.raises(DomainError, match="No tasks available"):
            pull_stantion_task(PullStantionTaskRequest(hardware_id="hw-001"))


# ---------------------------------------------------------------------------
# Tests: accept_stantion_task
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestAcceptStantionTask:
    def test_accepts_reserved_task(
        self, reserved_task: StantionTaskModel
    ) -> None:
        data = AcceptStantionTaskRequest(
            hardware_id="hw-001",
            task_id=reserved_task.id,
        )

        result = accept_stantion_task(data)

        assert result.id == reserved_task.id
        result.refresh_from_db()
        assert result.status_enum == TaskStatusEnum.ACCEPTED

    def test_raises_when_task_not_found(
        self, stantion: RegisteredStantionModel
    ) -> None:
        data = AcceptStantionTaskRequest(
            hardware_id="hw-001",
            task_id=uuid.uuid4(),
        )

        with pytest.raises(DomainError, match="RESERVED"):
            accept_stantion_task(data)

    def test_raises_when_task_not_in_reserved_status(
        self, created_task: StantionTaskModel
    ) -> None:
        data = AcceptStantionTaskRequest(
            hardware_id="hw-001",
            task_id=created_task.id,
        )

        with pytest.raises(DomainError, match="RESERVED"):
            accept_stantion_task(data)


# ---------------------------------------------------------------------------
# Tests: complete_stantion_task
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestCompleteStantionTask:
    def test_completes_release_battery_task_success(
        self, accepted_task: StantionTaskModel
    ) -> None:
        data = CreateStantionTaskResultRequest(
            hardware_id="hw-001",
            task_id=accepted_task.id,
            result=ReleaseBatteryTaskResult(success=True),
        )

        result = complete_stantion_task(data)

        result.refresh_from_db()
        assert result.status_enum == TaskStatusEnum.COMPLETED
        assert result.response_release_battery_success is True
        assert result.response_release_battery_error == ""

    def test_complete_release_battery_stores_error_message(
        self, accepted_task: StantionTaskModel
    ) -> None:
        data = CreateStantionTaskResultRequest(
            hardware_id="hw-001",
            task_id=accepted_task.id,
            result=ReleaseBatteryTaskResult(success=False, error="slot jam"),
        )

        result = complete_stantion_task(data)

        result.refresh_from_db()
        assert result.status_enum == TaskStatusEnum.FAILED
        assert result.response_release_battery_error == "slot jam"

    def test_completes_receive_battery_task_with_new_battery(
        self,
        accepted_task: StantionTaskModel,
        battery_type: BatteryTypeModel,
    ) -> None:
        data = CreateStantionTaskResultRequest(
            hardware_id="hw-001",
            task_id=accepted_task.id,
            result=ReceiveBatteryTaskResult(
                success=True,
                received_battery=BatteryInfo(
                    hardware_id="bat-received", model_name="bat-v1"
                ),
            ),
        )

        result = complete_stantion_task(data)

        result.refresh_from_db()
        assert result.status_enum == TaskStatusEnum.COMPLETED
        assert result.response_receive_battery_success is True
        assert RegisteredBatteryModel.objects.filter(
            hardware_id="bat-received"
        ).exists()

    def test_completes_receive_battery_task_without_battery(
        self, accepted_task: StantionTaskModel
    ) -> None:
        data = CreateStantionTaskResultRequest(
            hardware_id="hw-001",
            task_id=accepted_task.id,
            result=ReceiveBatteryTaskResult(success=True, received_battery=None),
        )

        result = complete_stantion_task(data)

        result.refresh_from_db()
        assert result.status_enum == TaskStatusEnum.COMPLETED
        assert result.response_receive_battery_success is True

    def test_receive_battery_task_failure_marks_failed(
        self, accepted_task: StantionTaskModel
    ) -> None:
        data = CreateStantionTaskResultRequest(
            hardware_id="hw-001",
            task_id=accepted_task.id,
            result=ReceiveBatteryTaskResult(success=False, error="sensor error"),
        )

        result = complete_stantion_task(data)

        result.refresh_from_db()
        assert result.status_enum == TaskStatusEnum.FAILED
        assert result.response_receive_battery_error == "sensor error"

    def test_raises_when_task_not_found(
        self, stantion: RegisteredStantionModel
    ) -> None:
        data = CreateStantionTaskResultRequest(
            hardware_id="hw-001",
            task_id=uuid.uuid4(),
            result=ReleaseBatteryTaskResult(success=True),
        )

        with pytest.raises(DomainError, match="ACCEPTED"):
            complete_stantion_task(data)

    def test_raises_when_task_not_in_accepted_status(
        self, reserved_task: StantionTaskModel
    ) -> None:
        data = CreateStantionTaskResultRequest(
            hardware_id="hw-001",
            task_id=reserved_task.id,
            result=ReleaseBatteryTaskResult(success=True),
        )

        with pytest.raises(DomainError, match="ACCEPTED"):
            complete_stantion_task(data)
