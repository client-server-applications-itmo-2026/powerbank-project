from ninja import Schema


class UpdateAuthenticatedUserRequest(Schema):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    patronymic_name: str | None = None
    phone_number: str | None = None


class RegisterUserRequest(Schema):
    email: str
    password: str
    re_password: str
    first_name: str
    last_name: str
    patronymic_name: str | None
    phone_number: str | None
