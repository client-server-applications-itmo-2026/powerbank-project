from typing import TYPE_CHECKING

from django.utils import timezone

from server.apps.rentals.models import RentalModel, RentalStatusEnum
from server.apps.stantions.models import TaskTypeEnum

if TYPE_CHECKING:
    from server.apps.stantions.models import StantionTaskModel


def handle_complete_success_task(task_instance: "StantionTaskModel") -> None:
    if task_instance.task_type is not TaskTypeEnum.RECEIVE_BATTERY:
        return

    rental_instance = RentalModel.objects.get(related_accept_task=task_instance)
    rental_instance.status = RentalStatusEnum.COMPLETED
    rental_instance.completed_at = timezone.now()
    rental_instance.save()
