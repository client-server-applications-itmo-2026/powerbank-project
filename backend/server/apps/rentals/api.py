from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate

from server.apps.rentals.logic import functions as domain_functions
from server.apps.rentals.logic.response_schemas import RentalSchema

router = Router()


@router.post("/retnals", tags=["rentals"], response=RentalSchema)
def retrieve_rental_by_id(request, rental_id: int):
    return domain_functions.retrieve_rental_by_id(rental_id, request.auth)


@router.get("/me/rentals", tags=["rentals"], response=list[RentalSchema])
@paginate(LimitOffsetPagination)
def retrieve_rentals_by_user(request):
    return domain_functions.retrieve_rentals_by_user(request.auth)


@router.post("/start-rental", tags=["rentals"], response=RentalSchema)
def start_rental(request, data: domain_functions.StartRentalRequest):
    return domain_functions.start_rental(request.auth, data)


@router.post("/complete-rental", tags=["rentals"], response=RentalSchema)
def complete_rental(request, data: domain_functions.CompleteRentalRequest):
    return domain_functions.complete_rental(request.auth, data)
