from ninja import Schema


class UpdateAuthenticatedUserSchema(Schema):
    email: str | None
    first_name: str | None
    last_name: str | None
    patronymic_name: str | None
    phone_number: str | None
