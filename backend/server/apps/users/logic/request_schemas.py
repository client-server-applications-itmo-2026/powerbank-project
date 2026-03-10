from ninja import Schema
from pydantic import model_validator


class UpdateAuthenticatedUserRequest(Schema):
    email: str | None
    first_name: str | None
    last_name: str | None
    patronymic_name: str | None
    phone_number: str | None


class RegisterUserRequest(Schema):
    email: str
    password: str
    re_password: str
    first_name: str
    last_name: str
    patronymic_name: str | None
    phone_number: str | None
