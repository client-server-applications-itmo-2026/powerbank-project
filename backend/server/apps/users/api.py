from ninja import Router

from .logic import functions as domain_functions
from .logic.request_schemas import UpdateAuthenticatedUserSchema
from .logic.response_schemas import UserRetrieveResponse

router = Router()


@router.get("/me", response=UserRetrieveResponse)
def get_me(request) -> UserRetrieveResponse:
    return UserRetrieveResponse.model_validate(request.auth)


@router.patch("/me", response=UserRetrieveResponse)
def update_me(request, data: UpdateAuthenticatedUserSchema):
    updated_user = domain_functions.update_user(data, request.auth)
    return UserRetrieveResponse.model_validate(updated_user)
