from ninja import Router

from .logic import functions as domain_functions
from .logic.request_schemas import RegisterUserRequest, UpdateAuthenticatedUserRequest
from .logic.response_schemas import UserRetrieveResponse

router = Router()


@router.get("/me", response=UserRetrieveResponse)
def get_me(request) -> UserRetrieveResponse:
    return UserRetrieveResponse.model_validate(request.auth)


@router.patch("/me", response=UserRetrieveResponse)
def update_me(request, data: UpdateAuthenticatedUserRequest):
    updated_user = domain_functions.update_user(data, request.auth)
    return UserRetrieveResponse.model_validate(updated_user)


@router.post("/register", auth=None, response=UserRetrieveResponse)
def register_user(request, data: RegisterUserRequest):
    return domain_functions.register_user(data)
