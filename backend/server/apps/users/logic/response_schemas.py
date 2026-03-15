import datetime

from ninja import Schema


class UserRetrieveResponse(Schema):
    id: int
    email: str
    first_name: str
    last_name: str
    patronymic_name: str | None
    phone_number: str | None
    is_stantion_admin: bool
    is_staff: bool
    is_superuser: bool
    date_joined: datetime.datetime
    updated_at: datetime.datetime
    avatar_url: str | None = None
