import datetime
from typing import final

import pytest
from django.contrib.gis.geos import Point as GeoPoint

from server.apps.rentals.logic.functions import (
    complete_rental,
    count_price,
    retrieve_rental_by_id,
    retrieve_rentals_by_user,
    start_rental,
)
from server.apps.rentals.logic.request_schemas import (
    CompleteRentalRequest,
    StartRentalRequest,
)
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
from server.common.exceptions import DomainError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db) -> UserModel:
    return UserModel.objects.create_user(
        email="user@example.com", password="pass"  # noqa: S106
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
        hardware_id="1",
        stantion_type=stantion_type,
        location=GeoPoint(37.6173, 55.7558, srid=4326),
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
        name="Test Tariff",
        price_per_tick=100,
        tariff_type=TarrifTypeEnum.FIXED,
    )


@pytest.fixture
def heartbeat_with_charged_battery(
    stantion: RegisteredStantionModel,
    battery: RegisteredBatteryModel,
) -> StantionHeartBeatModel:
    heartbeat = StantionHeartBeatModel.objects.create(registered_stantion=stantion)
    HeartBeatSlotStateModel.objects.create(
        heartbeat=heartbeat,
        state=SlotStateEnum.CHARGED,
        slot_index=0,
        registered_battery=battery,
    )
    return heartbeat


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


# ---------------------------------------------------------------------------
# Tests: retrieve_rental_by_id
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestRetrieveRentalById:
    def test_returns_rental_when_exists(
        self, active_rental: RentalModel, user: UserModel
    ) -> None:
        result = retrieve_rental_by_id(active_rental.id, user)

        assert result.id == active_rental.id

    def test_raises_domain_error_when_not_found(self, user: UserModel) -> None:
        with pytest.raises(DomainError, match="does not exist"):
            retrieve_rental_by_id(99999, user)
    def test_does_not_return_rental_of_other_user(
        self,
        active_rental: RentalModel,
        user: UserModel,
    ) -> None:
        other_user = UserModel.objects.create_user(
            email="other@example.com",
            password="pass",  # noqa: S106
        )
    
        with pytest.raises(DomainError):
            retrieve_rental_by_id(active_rental.id, other_user)


# ---------------------------------------------------------------------------
# Tests: retrieve_rentals_by_user
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestRetrieveRentalsByUser:
    def test_returns_rentals_for_user(
        self, active_rental: RentalModel, user: UserModel
    ) -> None:
        result = retrieve_rentals_by_user(user)

        assert result.count() == 1
        assert result.first().id == active_rental.id  # type: ignore

    def test_returns_empty_queryset_when_no_rentals(self, user: UserModel) -> None:
        result = retrieve_rentals_by_user(user)

        assert result.count() == 0

    def test_does_not_include_rentals_of_other_users(
        self,
        active_rental: RentalModel,
        user: UserModel,
        stantion: RegisteredStantionModel,
        battery: RegisteredBatteryModel,
        tariff: TariffModel,
    ) -> None:
        other_user = UserModel.objects.create_user(
            email="other@example.com", password="pass"  # noqa: S106
        )
        RentalModel.objects.create(
            user=other_user,
            battery=battery,
            tariff=tariff,
            started_at_stantion=stantion,
            status=RentalStatusEnum.ACTIVE,
        )

        result = retrieve_rentals_by_user(user)

        assert result.count() == 1

    def test_returns_all_rentals_for_user(
        self,
        user: UserModel,
        stantion: RegisteredStantionModel,
        battery: RegisteredBatteryModel,
        tariff: TariffModel,
    ) -> None:
        RentalModel.objects.create(
            user=user,
            battery=battery,
            tariff=tariff,
            started_at_stantion=stantion,
            status=RentalStatusEnum.COMPLETED,
        )
        RentalModel.objects.create(
            user=user,
            battery=battery,
            tariff=tariff,
            started_at_stantion=stantion,
            status=RentalStatusEnum.ACTIVE,
        )

        result = retrieve_rentals_by_user(user)

        assert result.count() == 2
    def test_returns_queryset(self, user: UserModel) -> None:
        result = retrieve_rentals_by_user(user)
    
        from django.db.models.query import QuerySet
    
        assert isinstance(result, QuerySet)


# ---------------------------------------------------------------------------
# Tests: count_price
# ---------------------------------------------------------------------------


@final
class TestCountPrice:
    def test_fixed_tariff_always_returns_price_per_tick(self) -> None:
        tariff = TariffModel(price_per_tick=500, tariff_type=TarrifTypeEnum.FIXED)

        result = count_price(tariff, datetime.timedelta(hours=10))

        assert result == 500

    def test_per_day_tariff_counts_full_days_plus_one(self) -> None:
        tariff = TariffModel(price_per_tick=100, tariff_type=TarrifTypeEnum.PER_DAY)

        result = count_price(tariff, datetime.timedelta(days=2))

        assert result == 300  # (2 days + 1) * 100

    def test_per_day_tariff_partial_day_counts_as_one_tick(self) -> None:
        tariff = TariffModel(price_per_tick=100, tariff_type=TarrifTypeEnum.PER_DAY)

        result = count_price(tariff, datetime.timedelta(hours=6))

        assert result == 100  # (0 full days + 1) * 100

    def test_per_hour_tariff(self) -> None:
        tariff = TariffModel(price_per_tick=50, tariff_type=TarrifTypeEnum.PER_HOUR)

        result = count_price(tariff, datetime.timedelta(hours=3))

        assert result == 200  # (3 hours + 1) * 50

    def test_per_hour_tariff_partial_hour_rounds_down(self) -> None:
        tariff = TariffModel(price_per_tick=50, tariff_type=TarrifTypeEnum.PER_HOUR)

        result = count_price(tariff, datetime.timedelta(minutes=90))

        assert result == 100  # (1 full hour + 1) * 50

    def test_per_minute_tariff(self) -> None:
        tariff = TariffModel(price_per_tick=10, tariff_type=TarrifTypeEnum.PER_MINUTE)

        result = count_price(tariff, datetime.timedelta(minutes=30))

        assert result == 310  # (30 minutes + 1) * 10

    def test_raises_domain_error_for_unknown_tariff_type(self) -> None:
        tariff = TariffModel(price_per_tick=100, tariff_type="UNKNOWN")

        with pytest.raises(DomainError, match="Unknown tariff type"):
            count_price(tariff, datetime.timedelta(hours=1))

    def test_per_minute_tariff_zero_duration(self) -> None:
        tariff = TariffModel(price_per_tick=10, tariff_type=TarrifTypeEnum.PER_MINUTE)
    
        result = count_price(tariff, datetime.timedelta())
    
        assert result == 10 # duration = 0


# ---------------------------------------------------------------------------
# Tests: start_rental
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestStartRental:
    def test_creates_rental_with_correct_data(
        self,
        user: UserModel,
        stantion: RegisteredStantionModel,
        battery: RegisteredBatteryModel,
        tariff: TariffModel,
        heartbeat_with_charged_battery: StantionHeartBeatModel,
    ) -> None:
        data = StartRentalRequest(stantion_id=stantion.hardware_id, tariff_id=tariff.id)

        result = start_rental(user, data)

        assert isinstance(result, RentalModel)
        assert result.user == user
        assert result.tariff == tariff
        assert result.started_at_stantion == stantion
        assert result.status == RentalStatusEnum.INITIALIZING
        assert RentalModel.objects.filter(id=result.id).exists()

    def test_raises_when_stantion_not_found(
        self, user: UserModel, tariff: TariffModel
    ) -> None:
        data = StartRentalRequest(stantion_id="99999", tariff_id=tariff.id)

        with pytest.raises(RegisteredStantionModel.DoesNotExist):
            start_rental(user, data)

    def test_raises_when_tariff_not_found(
        self, user: UserModel, stantion: RegisteredStantionModel
    ) -> None:
        data = StartRentalRequest(stantion_id=stantion.hardware_id, tariff_id=99999)

        with pytest.raises(TariffModel.DoesNotExist):
            start_rental(user, data)

    def test_raises_when_stantion_has_no_active_heartbeat(
        self,
        user: UserModel,
        stantion: RegisteredStantionModel,
        tariff: TariffModel,
    ) -> None:
        data = StartRentalRequest(stantion_id=stantion.hardware_id, tariff_id=tariff.id)

        with pytest.raises(DomainError, match="Stantion is not active"):
            start_rental(user, data)

    def test_raises_when_no_charged_batteries(
        self,
        user: UserModel,
        stantion: RegisteredStantionModel,
        tariff: TariffModel,
    ) -> None:
        heartbeat = StantionHeartBeatModel.objects.create(registered_stantion=stantion)
        HeartBeatSlotStateModel.objects.create(
            heartbeat=heartbeat,
            state=SlotStateEnum.EMPTY,
            slot_index=0,
        )
        data = StartRentalRequest(stantion_id=stantion.hardware_id, tariff_id=tariff.id)

        with pytest.raises(DomainError, match="No charged batteries"):
            start_rental(user, data)


# ---------------------------------------------------------------------------
# Tests: complete_rental
# ---------------------------------------------------------------------------


@final
@pytest.mark.django_db
class TestCompleteRental:
    def test_completes_active_rental(
        self,
        user: UserModel,
        active_rental: RentalModel,
        stantion: RegisteredStantionModel,
    ) -> None:
        data = CompleteRentalRequest(
            rental_id=active_rental.id, stantion_id=stantion.hardware_id
        )

        result = complete_rental(user, data)

        assert result.status == RentalStatusEnum.WAIT_FOR_COMPLETION
        assert result.completed_at_stantion == stantion
        assert result.final_price is not None
        assert result.related_accept_task is not None

    def test_raises_when_rental_is_not_active(
        self,
        user: UserModel,
        active_rental: RentalModel,
        stantion: RegisteredStantionModel,
    ) -> None:
        active_rental.status = RentalStatusEnum.COMPLETED
        active_rental.save()
        data = CompleteRentalRequest(
            rental_id=active_rental.id, stantion_id=stantion.hardware_id
        )

        with pytest.raises(DomainError, match="Only active rentals can be completed"):
            complete_rental(user, data)

    def test_raises_when_rental_not_found(
        self, user: UserModel, stantion: RegisteredStantionModel
    ) -> None:
        data = CompleteRentalRequest(rental_id=99999, stantion_id=stantion.hardware_id)

        with pytest.raises(RentalModel.DoesNotExist):
            complete_rental(user, data)

    def test_user_cannot_complete_rental_of_another_user(
        self,
        active_rental: RentalModel,
        stantion: RegisteredStantionModel,
    ) -> None:
        other_user = UserModel.objects.create_user(
            email="other@example.com",
            password="pass",
        )
    
        data = CompleteRentalRequest(
            rental_id=active_rental.id,
            stantion_id=stantion.hardware_id,
        )
    
        with pytest.raises(DomainError):
            complete_rental(other_user, data)

    def test_raises_when_completion_stantion_not_found(
        self,
        user: UserModel,
        active_rental: RentalModel,
    ) -> None:
        data = CompleteRentalRequest(rental_id=active_rental.id, stantion_id="99999")

        with pytest.raises(RegisteredStantionModel.DoesNotExist):
            complete_rental(user, data)
