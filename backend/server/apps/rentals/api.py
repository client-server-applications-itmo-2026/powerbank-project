from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate

from server.apps.rentals.logic import functions as domain_functions
from server.apps.rentals.logic.response_schemas import RentalSchema

router = Router()


@router.post("/start", tags=["rentals"], response=RentalSchema)
def retrieve_rental_by_id(request, rental_id: int):
    return domain_functions.retrieve_rental_by_id(rental_id, request.auth.user)


@router.get("/my", tags=["rentals"], response=list[RentalSchema])
@paginate(LimitOffsetPagination)
def retrieve_rentals_by_user(request):
    return domain_functions.retrieve_rentals_by_user(request.auth.user)


@router.post("/start-rental", tags=["rentals"], response=RentalSchema)
def start_rental(request, data: domain_functions.StartRentalRequest):
    return domain_functions.start_rental(request.auth.user, data)


@router.post("/complete-rental", tags=["rentals"], response=RentalSchema)
def complete_rental(request, data: domain_functions.CompleteRentalRequest):
    return domain_functions.complete_rental(request.auth.user, data)
