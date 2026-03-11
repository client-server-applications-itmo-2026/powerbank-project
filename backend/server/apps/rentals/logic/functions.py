import datetime

from django.db.models import QuerySet
from django.utils import timezone

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
from server.apps.stantions.logic.public import (
    create_receive_battery_task,
    create_release_battery_task,
)
from server.apps.stantions.models import (
    RegisteredStantionModel,
)
from server.apps.users.models import UserModel
from server.common.exceptions import DomainError


def retrieve_rental_by_id(rental_id: int, auth_user: UserModel) -> RentalModel:
    try:
        return RentalModel.objects.get(id=rental_id)
    except RentalModel.DoesNotExist:
        raise DomainError(f"Rental with id {rental_id} does not exist")


def retrieve_rentals_by_user(user: UserModel) -> QuerySet[RentalModel]:
    return (
        RentalModel.objects.filter(user=user)
        .select_related(
            "started_at_stantion",
            "completed_at_stantion",
            "battery",
            "tariff",
        )
        .order_by("-started_at")
    )


def start_rental(user: UserModel, data: StartRentalRequest) -> RentalModel:
    stantion_instance = RegisteredStantionModel.objects.get(
        hardware_id=data.stantion_id, is_active=True, is_deleted=False
    )
    tariff_instance = TariffModel.objects.get(id=data.tariff_id, is_active=True)
    release_battery_task = create_release_battery_task(
        stantion_instance=stantion_instance
    )
    return RentalModel.objects.create(
        user=user,
        battery=release_battery_task.payload_release_battery,  # type: ignore
        related_release_task=release_battery_task,
        tariff=tariff_instance,
        started_at_stantion=stantion_instance,
        status=RentalStatusEnum.INITIALIZING,
    )


PRICE_CALCULATORS_REGISTRY = {
    TarrifTypeEnum.FIXED: lambda tariff, rental_timedelta: tariff.price_per_tick,
    TarrifTypeEnum.PER_DAY: lambda tariff, rental_timedelta: tariff.price_per_tick
    * (rental_timedelta.days + 1),
    TarrifTypeEnum.PER_HOUR: lambda tariff, rental_timedelta: tariff.price_per_tick
    * (rental_timedelta.total_seconds() // 3600 + 1),
    TarrifTypeEnum.PER_MINUTE: lambda tariff, rental_timedelta: tariff.price_per_tick
    * (rental_timedelta.total_seconds() // 60 + 1),
}


def count_price(tariff: TariffModel, rental_timedelta: datetime.timedelta) -> int:
    if tariff.tariff_type not in PRICE_CALCULATORS_REGISTRY:
        raise DomainError("Unknown tariff type")

    price_calculator = PRICE_CALCULATORS_REGISTRY[tariff.tariff_type]
    return price_calculator(tariff, rental_timedelta)


def complete_rental(user: UserModel, data: CompleteRentalRequest) -> RentalModel:
    rental_instance = RentalModel.objects.get(id=data.rental_id, user=user)
    if rental_instance.status != RentalStatusEnum.ACTIVE:
        raise DomainError("Only active rentals can be completed")

    stantion_instance = RegisteredStantionModel.objects.get(
        hardware_id=data.stantion_id, is_active=True, is_deleted=False
    )

    rental_instance.completed_at_stantion = stantion_instance
    task_instance = create_receive_battery_task(stantion_instance=stantion_instance)

    rental_instance.related_accept_task = task_instance
    rental_instance.status = RentalStatusEnum.WAIT_FOR_COMPLETION
    rental_instance.final_price = count_price(
        rental_instance.tariff,
        timezone.now() - rental_instance.started_at,
    )

    rental_instance.save()

    return rental_instance
