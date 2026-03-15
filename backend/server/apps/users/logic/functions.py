from server.apps.users.logic.request_schemas import (
    RegisterUserRequest,
    UpdateAuthenticatedUserRequest,
)
from server.apps.users.models import UserModel
from server.common.exceptions import DomainError

# Хз, постараюсь сделать по минимуму оверхеда, но хоть было чуть-чуть поддерживаемое


class PasswordIncorrectError(DomainError):

    def __init__(self, **context) -> None:
        super().__init__("Passwords do not match", **context)


class ProfileAlreadyExistsError(DomainError):

    def __init__(self, **idents) -> None:
        if "email" in idents:
            msg = "A profile with this email is already registered."
        elif "phone_number" in idents:
            msg = "A profile with this phone number is already registered."
        else:
            msg = f"A profile with these details already exists: {idents}"
        super().__init__(msg, **idents)


def update_user(
    data: UpdateAuthenticatedUserRequest, auth_user: UserModel
) -> UserModel:
    updated_data = data.model_dump(exclude_unset=True)
    if "email" in updated_data and updated_data["email"]:
        other = UserModel.objects.filter(email=updated_data["email"]).exclude(pk=auth_user.pk)
        if other.exists():
            raise ProfileAlreadyExistsError(email=updated_data["email"])
    if "phone_number" in updated_data and updated_data["phone_number"]:
        cleaned = _clean_phone_number(updated_data["phone_number"])
        other = UserModel.objects.filter(phone_number=cleaned).exclude(pk=auth_user.pk)
        if other.exists():
            raise ProfileAlreadyExistsError(phone_number=cleaned)
    for field, value in updated_data.items():
        if field == "phone_number" and value:
            value = _clean_phone_number(value)
        setattr(auth_user, field, value)
    auth_user.save()
    return auth_user


def _clean_phone_number(phone_number: str) -> str:
    numbers = filter(str.isalnum, phone_number)
    return "+" + "".join(numbers)


def register_user(data: RegisterUserRequest) -> UserModel:

    if data.password != data.re_password:
        raise PasswordIncorrectError()

    if UserModel.objects.filter(email=data.email).exists():
        ctx = {"email": data.email}
        raise ProfileAlreadyExistsError(**ctx)

    if data.phone_number and UserModel.objects.filter(
        phone_number=data.phone_number
    ).exists():
        ctx = {"phone_number": data.phone_number}
        raise ProfileAlreadyExistsError(**ctx)

    creation_data = data.model_dump(exclude_unset=True)
    creation_data.pop("re_password", None)
    if creation_data.get("phone_number"):
        creation_data["phone_number"] = _clean_phone_number(
            phone_number=creation_data["phone_number"]
        )

    return UserModel.objects.create_user(**creation_data)
