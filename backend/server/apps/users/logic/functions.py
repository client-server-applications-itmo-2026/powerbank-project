from server.apps.users.logic.request_schemas import (
    RegisterUserRequest,
    UpdateAuthenticatedUserRequest,
)
from server.apps.users.models import UserModel
from server.common.exceptions import DomainError

# Хз, постараюсь сделать по минимуму оверхеда, но хоть было чуть-чуть поддерживаемое


class PasswordIncorrectError(DomainError):

    def __init__(self, **context) -> None:
        super().__init__("Passwords does not match", **context)


class ProfileAlreadyExistsError(DomainError):

    def __init__(self, **idents) -> None:
        super().__init__(f"Profile with idents: {idents} already existst", **idents)


def update_user(
    data: UpdateAuthenticatedUserRequest, auth_user: UserModel
) -> UserModel:
    updated_data = data.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(auth_user, field, value)
    auth_user.save()
    return auth_user


def _clean_phone_number(phone_number: str) -> str:
    numbers = filter(str.isalnum, phone_number)
    return "+" + "".join(numbers)


def register_user(data: RegisterUserRequest) -> UserModel:

    if data.password != data.re_password:
        raise PasswordIncorrectError

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
