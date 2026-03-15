from django.conf import settings
from django.core.files.base import ContentFile
from ninja import File, Router
from ninja.files import UploadedFile

from .logic import functions as domain_functions
from .logic.request_schemas import (
    RegisterUserRequest,
    UpdateAuthenticatedUserRequest,
)
from .logic.response_schemas import UserRetrieveResponse

router = Router()


def _build_user_response(user, request) -> UserRetrieveResponse:
    """Build UserRetrieveResponse with avatar_url as absolute URL (works behind proxy)."""
    data = UserRetrieveResponse.model_validate(user).model_dump()
    if getattr(user, "avatar", None) and user.avatar:
        base = getattr(settings, "PUBLIC_BASE_URL", "") or ""
        if base:
            data["avatar_url"] = base.rstrip("/") + user.avatar.url
        else:
            data["avatar_url"] = request.build_absolute_uri(user.avatar.url)
    else:
        data["avatar_url"] = None
    return UserRetrieveResponse(**data)


@router.get("/me", response=UserRetrieveResponse)
def get_me(request) -> UserRetrieveResponse:
    return _build_user_response(request.auth, request)


@router.patch("/me", response=UserRetrieveResponse)
def update_me(request, data: UpdateAuthenticatedUserRequest):
    updated_user = domain_functions.update_user(data, request.auth)
    return _build_user_response(updated_user, request)


@router.post("/me/avatar", response=UserRetrieveResponse)
def upload_avatar(request, file: File[UploadedFile]):
    """Update the authenticated user's avatar. Accepts image file (e.g. image/jpeg, image/png)."""
    user = request.auth
    name = file.name or "avatar"
    user.avatar.save(name, ContentFile(file.read()), save=True)
    return _build_user_response(user, request)


@router.post("/register", auth=None, response=UserRetrieveResponse)
def register_user(request, data: RegisterUserRequest):
    new_user = domain_functions.register_user(data)
    return _build_user_response(new_user, request)
